from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Ticket
from ..rbac import READ_ROLES, assert_can_approve, require_role
from ..schemas import AuditLogResponse, Employee, ReviewRequest, ReviewResponse
from ..service_clients import get_current_user
from ..workflow import add_audit, latest_draft, record_review

router = APIRouter(prefix="/tickets", tags=["reviews"])


def _ticket_or_404(db: Session, ticket_id: str) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).one_or_none()
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.post("/{ticket_id}/review", response_model=ReviewResponse)
def review_ticket(
    ticket_id: str,
    payload: ReviewRequest,
    db: Session = Depends(get_db),
    user: Employee = Depends(get_current_user),
) -> ReviewResponse:
    require_role(user, {"CS_AGENT", "SUPERVISOR", "ADMIN"})
    ticket = _ticket_or_404(db, ticket_id)
    draft = latest_draft(ticket)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft required before review")
    action = payload.action.upper()
    risk_level = draft.draft.get("risk_level", "LOW")
    if action == "APPROVE":
        try:
            assert_can_approve(user, risk_level)
        except HTTPException:
            add_audit(db, ticket.ticket_id, user, "review_approve", "denied", {"risk_level": risk_level})
            db.commit()
            raise
    elif action not in {"REJECT", "REQUEST_SUPERVISOR", "CLOSE"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported review action")
    record_review(db, ticket, user, action, payload.comment, payload.edited_draft_response)
    add_audit(db, ticket.ticket_id, user, f"review_{action.lower()}", "success", {"risk_level": risk_level})
    db.commit()
    return ReviewResponse(ticket_id=ticket.ticket_id, action=action, status=ticket.status)


@router.get("/{ticket_id}/audit", response_model=list[AuditLogResponse])
def get_audit(ticket_id: str, db: Session = Depends(get_db), user: Employee = Depends(get_current_user)) -> list[AuditLogResponse]:
    require_role(user, READ_ROLES)
    if user.role == "CS_AGENT":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Audit log requires supervisor, auditor, or admin")
    ticket = _ticket_or_404(db, ticket_id)
    return [
        AuditLogResponse(
            ticket_id=item.ticket_id,
            action=item.action,
            status=item.status,
            actor_employee_id=item.actor_employee_id,
            actor_role=item.actor_role,
            details=item.details,
        )
        for item in sorted(ticket.audit_logs, key=lambda log: log.created_at)
    ]


from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from .models import Draft, RetrievedEvidence, ReviewAction, Ticket, TicketAnalysis, WorkflowAuditLog
from .schemas import Employee


def add_audit(db: Session, ticket_id: str, user: Employee, action: str, status: str, details: dict[str, Any] | None = None) -> None:
    db.add(
        WorkflowAuditLog(
            ticket_id=ticket_id,
            actor_employee_id=user.employee_id,
            actor_role=user.role,
            action=action,
            status=status,
            details=details or {},
        )
    )


def save_analysis(db: Session, ticket: Ticket, classification: dict[str, Any], urgency: dict[str, Any], evidence: list[dict[str, Any]]) -> TicketAnalysis:
    if ticket.analysis is None:
        analysis = TicketAnalysis(ticket_id=ticket.ticket_id, classification=classification, urgency=urgency)
        db.add(analysis)
    else:
        analysis = ticket.analysis
        analysis.classification = classification
        analysis.urgency = urgency
    for item in list(ticket.evidence):
        db.delete(item)
    for item in evidence:
        db.add(
            RetrievedEvidence(
                ticket_id=ticket.ticket_id,
                policy_id=item["policy_id"],
                chunk_id=item["chunk_id"],
                title=item.get("title", ""),
                section=item.get("section", ""),
                score=float(item.get("score", 0)),
                text=item.get("text", ""),
                item_metadata=item.get("metadata", {}),
            )
        )
    ticket.status = "NEEDS_INFO" if not evidence else "ANALYZING"
    return analysis


def evidence_to_context(ticket: Ticket) -> list[dict[str, Any]]:
    return [
        {
            "policy_id": item.policy_id,
            "chunk_id": item.chunk_id,
            "title": item.title,
            "section": item.section,
            "score": item.score,
            "text": item.text,
            "metadata": item.item_metadata,
        }
        for item in ticket.evidence
    ]


def save_draft(db: Session, ticket: Ticket, draft_payload: dict[str, Any]) -> Draft:
    draft_body = draft_payload.get("draft", draft_payload)
    draft = Draft(ticket_id=ticket.ticket_id, draft=draft_body)
    db.add(draft)
    risk_level = draft_body.get("risk_level", "LOW")
    missing_info = draft_body.get("missing_info") or []
    if not ticket.evidence or (missing_info and risk_level not in {"CRITICAL", "HIGH"}):
        ticket.status = "NEEDS_INFO"
    elif risk_level in {"CRITICAL", "HIGH"} or draft_body.get("requires_supervisor_approval"):
        ticket.status = "PENDING_SUPERVISOR"
    else:
        ticket.status = "DRAFT_READY"
    return draft


def latest_draft(ticket: Ticket) -> Draft | None:
    if not ticket.drafts:
        return None
    return sorted(ticket.drafts, key=lambda draft: draft.created_at)[-1]


def record_review(
    db: Session,
    ticket: Ticket,
    user: Employee,
    action: str,
    comment: str | None,
    edited_draft_response: str | None,
) -> ReviewAction:
    review = ReviewAction(
        ticket_id=ticket.ticket_id,
        employee_id=user.employee_id,
        role=user.role,
        action=action,
        comment=comment,
    )
    db.add(review)
    draft = latest_draft(ticket)
    if edited_draft_response and draft is not None:
        draft.edited_draft_response = edited_draft_response
    if action == "APPROVE":
        ticket.status = "APPROVED"
    elif action == "REJECT":
        ticket.status = "REJECTED"
    elif action == "CLOSE":
        ticket.status = "CLOSED"
    else:
        ticket.status = "PENDING_SUPERVISOR"
    return review


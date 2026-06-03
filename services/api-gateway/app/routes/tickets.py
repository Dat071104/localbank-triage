from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Ticket, WorkerJobResult
from ..privacy import redact_customer_text
from ..rbac import READ_ROLES, WRITE_ROLES, require_role
from ..schemas import AnalysisResponse, DraftResponse, Employee, TicketCreateRequest, TicketResponse, WorkerResultResponse
from ..service_clients import DownstreamClients, get_clients, get_current_user
from ..workflow import add_audit, evidence_to_context, save_analysis, save_draft

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _ticket_or_404(db: Session, ticket_id: str) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).one_or_none()
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def _ticket_response(ticket: Ticket) -> TicketResponse:
    return TicketResponse(
        ticket_id=ticket.ticket_id,
        customer_text=redact_customer_text(ticket.customer_text),
        status=ticket.status,
        created_by=ticket.created_by,
    )


@router.post("", response_model=TicketResponse)
def create_ticket(
    payload: TicketCreateRequest,
    db: Session = Depends(get_db),
    user: Employee = Depends(get_current_user),
) -> TicketResponse:
    require_role(user, {"CS_AGENT", "SUPERVISOR", "ADMIN"})
    if db.query(Ticket).filter(Ticket.ticket_id == payload.ticket_id).one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ticket_id already exists")
    ticket = Ticket(ticket_id=payload.ticket_id, customer_text=payload.customer_text, created_by=user.employee_id)
    db.add(ticket)
    add_audit(db, ticket.ticket_id, user, "create_ticket", "success", {"status": "NEW"})
    db.commit()
    db.refresh(ticket)
    return _ticket_response(ticket)


@router.get("", response_model=list[TicketResponse])
def list_tickets(
    db: Session = Depends(get_db),
    user: Employee = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[TicketResponse]:
    require_role(user, READ_ROLES)
    query = db.query(Ticket)
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    tickets = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
    return [_ticket_response(ticket) for ticket in tickets]


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db), user: Employee = Depends(get_current_user)) -> TicketResponse:
    require_role(user, READ_ROLES)
    return _ticket_response(_ticket_or_404(db, ticket_id))


@router.post("/{ticket_id}/analyze", response_model=AnalysisResponse)
def analyze_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    user: Employee = Depends(get_current_user),
    clients: DownstreamClients = Depends(get_clients),
) -> AnalysisResponse:
    require_role(user, WRITE_ROLES)
    ticket = _ticket_or_404(db, ticket_id)
    ticket.status = "ANALYZING"
    add_audit(db, ticket.ticket_id, user, "analyze", "started")
    try:
        classification = clients.classify(ticket.ticket_id, ticket.customer_text)
        urgency = clients.score_urgency(ticket.ticket_id, ticket.customer_text, classification)
        rag_response = clients.retrieve_evidence(ticket.ticket_id, ticket.customer_text, classification, urgency)
        evidence = rag_response.get("results", [])
        save_analysis(db, ticket, classification, urgency, evidence)
        add_audit(db, ticket.ticket_id, user, "analyze", "success", {"evidence_count": len(evidence)})
        db.commit()
    except Exception as exc:
        ticket.status = "FAILED"
        add_audit(db, ticket.ticket_id, user, "analyze", "failure", {"error_type": type(exc).__name__})
        db.commit()
        raise
    db.refresh(ticket)
    return AnalysisResponse(ticket_id=ticket.ticket_id, classification=classification, urgency=urgency, evidence=evidence_to_context(ticket))


@router.get("/{ticket_id}/analysis", response_model=AnalysisResponse)
def get_analysis(ticket_id: str, db: Session = Depends(get_db), user: Employee = Depends(get_current_user)) -> AnalysisResponse:
    require_role(user, READ_ROLES)
    ticket = _ticket_or_404(db, ticket_id)
    if ticket.analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return AnalysisResponse(
        ticket_id=ticket.ticket_id,
        classification=ticket.analysis.classification,
        urgency=ticket.analysis.urgency,
        evidence=evidence_to_context(ticket),
    )


@router.post("/{ticket_id}/draft", response_model=DraftResponse)
def create_draft(
    ticket_id: str,
    db: Session = Depends(get_db),
    user: Employee = Depends(get_current_user),
    clients: DownstreamClients = Depends(get_clients),
) -> DraftResponse:
    require_role(user, WRITE_ROLES)
    ticket = _ticket_or_404(db, ticket_id)
    if ticket.analysis is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Analyze ticket before drafting")
    try:
        draft_payload = clients.generate_draft(
            ticket.ticket_id,
            ticket.customer_text,
            ticket.analysis.classification,
            ticket.analysis.urgency,
            evidence_to_context(ticket),
        )
        draft = save_draft(db, ticket, draft_payload)
        add_audit(db, ticket.ticket_id, user, "draft", "success", {"status": ticket.status})
        db.commit()
    except Exception as exc:
        ticket.status = "FAILED"
        add_audit(db, ticket.ticket_id, user, "draft", "failure", {"error_type": type(exc).__name__})
        db.commit()
        raise
    db.refresh(draft)
    return DraftResponse(ticket_id=ticket.ticket_id, draft=draft.draft, edited_draft_response=draft.edited_draft_response)


@router.get("/{ticket_id}/draft", response_model=DraftResponse)
def get_draft(ticket_id: str, db: Session = Depends(get_db), user: Employee = Depends(get_current_user)) -> DraftResponse:
    require_role(user, READ_ROLES)
    ticket = _ticket_or_404(db, ticket_id)
    if not ticket.drafts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    draft = sorted(ticket.drafts, key=lambda item: item.created_at)[-1]
    return DraftResponse(ticket_id=ticket.ticket_id, draft=draft.draft, edited_draft_response=draft.edited_draft_response)


@router.get("/{ticket_id}/triage-result", response_model=WorkerResultResponse)
def get_triage_result(ticket_id: str, db: Session = Depends(get_db), user: Employee = Depends(get_current_user)) -> WorkerResultResponse:
    require_role(user, READ_ROLES)
    result = (
        db.query(WorkerJobResult)
        .filter(WorkerJobResult.ticket_id == ticket_id)
        .order_by(WorkerJobResult.updated_at.desc())
        .first()
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker result not found")
    return WorkerResultResponse(job_id=result.job_id, ticket_id=result.ticket_id, status=result.status, result=result.result)

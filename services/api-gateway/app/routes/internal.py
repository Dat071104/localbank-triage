from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..config import get_config
from ..db import get_db
from ..models import Ticket, WorkerJobResult
from ..schemas import WorkerResultRequest, WorkerResultResponse

router = APIRouter(tags=["internal"])


def require_worker_token(x_localbank_worker_token: str | None = Header(default=None)) -> None:
    expected = get_config().worker_internal_token
    if not expected or x_localbank_worker_token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid worker token")


@router.post("/internal/jobs/{job_id}/result", response_model=WorkerResultResponse)
def persist_worker_result(
    job_id: str,
    payload: WorkerResultRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_worker_token),
) -> WorkerResultResponse:
    existing = db.query(WorkerJobResult).filter(WorkerJobResult.job_id == job_id).one_or_none()
    if existing is None:
        existing = WorkerJobResult(
            job_id=job_id,
            ticket_id=payload.ticket_id,
            status=payload.status,
            result=payload.result,
        )
        db.add(existing)
    else:
        existing.ticket_id = payload.ticket_id
        existing.status = payload.status
        existing.result = payload.result

    ticket = db.query(Ticket).filter(Ticket.ticket_id == payload.ticket_id).one_or_none()
    if ticket is not None:
        ticket.status = payload.status

    db.commit()
    db.refresh(existing)
    return WorkerResultResponse(
        job_id=existing.job_id,
        ticket_id=existing.ticket_id,
        status=existing.status,
        result=existing.result,
    )

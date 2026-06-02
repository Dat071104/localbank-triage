from __future__ import annotations

from .celery_app import celery_app
from .pipeline import run_triage_pipeline
from .schemas import TriageJobRequest


@celery_app.task(name="localbank.triage_ticket")
def triage_ticket(payload: dict) -> dict:
    job = TriageJobRequest.model_validate(payload)
    return run_triage_pipeline(job).model_dump()


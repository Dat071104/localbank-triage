from __future__ import annotations

from fastapi import FastAPI

from .scorer import score_urgency
from .schemas import HealthResponse, UrgencyRequest, UrgencyResponse

app = FastAPI(title="LocalBank Urgency Service", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/score-urgency", response_model=UrgencyResponse)
def score(payload: UrgencyRequest) -> UrgencyResponse:
    return score_urgency(payload.ticket_id, payload.customer_text, payload.classification)

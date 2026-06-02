from __future__ import annotations

from fastapi import FastAPI

from .classifier import classify_ticket
from .schemas import ClassifyRequest, ClassifyResponse, HealthResponse

app = FastAPI(title="LocalBank Classifier Service", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/classify", response_model=ClassifyResponse)
def classify(payload: ClassifyRequest) -> ClassifyResponse:
    return classify_ticket(payload.ticket_id, payload.customer_text)

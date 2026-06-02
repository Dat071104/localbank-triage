from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str


class ClassifyRequest(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    customer_text: str = Field(min_length=1, max_length=4000)

    @field_validator("customer_text")
    @classmethod
    def validate_customer_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("customer_text must not be empty")
        return stripped


class ClassifyResponse(BaseModel):
    ticket_id: str
    intent: str
    intent_confidence: float
    sentiment: str
    sentiment_confidence: float
    model_version: str
    reason_codes: list[str]

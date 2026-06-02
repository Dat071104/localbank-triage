from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str


class ClassificationInput(BaseModel):
    intent: str
    intent_confidence: float = Field(ge=0, le=1)
    sentiment: str
    sentiment_confidence: float = Field(ge=0, le=1)
    reason_codes: list[str]


class UrgencyRequest(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    customer_text: str = Field(min_length=1, max_length=4000)
    classification: ClassificationInput

    @field_validator("customer_text")
    @classmethod
    def validate_customer_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("customer_text must not be empty")
        return stripped


class UrgencyResponse(BaseModel):
    ticket_id: str
    urgency_score: int
    urgency_level: str
    business_risk_score: int
    urgency_classifier_score: int
    intent_severity_score: int
    red_flag_rule_score: int
    sentiment_escalation_score: int
    reason_codes: list[str]
    requires_supervisor_approval: bool
    auto_send_allowed: bool

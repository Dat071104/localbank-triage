from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class TriageJobRequest(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    customer_text: str = Field(min_length=1, max_length=4000)

    @field_validator("customer_text")
    @classmethod
    def clean_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("customer_text must not be empty")
        return stripped


class StageError(BaseModel):
    stage: str
    error_type: str
    message: str


class PipelineResult(BaseModel):
    ticket_id: str
    status: str
    classification: dict[str, Any] | None = None
    urgency: dict[str, Any] | None = None
    retrieved_evidence: list[dict[str, Any]] = Field(default_factory=list)
    draft: dict[str, Any] | None = None
    errors: list[StageError] = Field(default_factory=list)
    requires_supervisor_approval: bool = False
    auto_send_allowed: bool = False


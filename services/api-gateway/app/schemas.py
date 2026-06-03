from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str


class Employee(BaseModel):
    employee_id: str
    role: str
    display_name: str | None = None


class TicketCreateRequest(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    customer_text: str = Field(min_length=1, max_length=4000)

    @field_validator("customer_text")
    @classmethod
    def clean_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("customer_text must not be empty")
        return stripped


class TicketResponse(BaseModel):
    ticket_id: str
    customer_text: str
    status: str
    created_by: str


class AnalysisResponse(BaseModel):
    ticket_id: str
    classification: dict[str, Any]
    urgency: dict[str, Any]
    evidence: list[dict[str, Any]]


class DraftResponse(BaseModel):
    ticket_id: str
    draft: dict[str, Any]
    edited_draft_response: str | None = None


class ReviewRequest(BaseModel):
    action: str
    comment: str | None = None
    edited_draft_response: str | None = None


class ReviewResponse(BaseModel):
    ticket_id: str
    action: str
    status: str


class AuditLogResponse(BaseModel):
    ticket_id: str
    action: str
    status: str
    actor_employee_id: str
    actor_role: str
    details: dict[str, Any]


class WorkerResultRequest(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    status: str = Field(min_length=1, max_length=32)
    result: dict[str, Any]


class WorkerResultResponse(BaseModel):
    job_id: str
    ticket_id: str
    status: str
    result: dict[str, Any]

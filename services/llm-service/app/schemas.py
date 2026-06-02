from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    backend: str
    prompt_version: str


class ClassificationInput(BaseModel):
    intent: str
    intent_confidence: float = Field(ge=0, le=1)
    sentiment: str
    sentiment_confidence: float = Field(ge=0, le=1)
    reason_codes: list[str] = Field(default_factory=list)


class UrgencyInput(BaseModel):
    urgency_score: int = Field(ge=0, le=100)
    urgency_level: str
    reason_codes: list[str] = Field(default_factory=list)
    requires_supervisor_approval: bool
    auto_send_allowed: bool


class PolicyMetadata(BaseModel):
    intent: str | None = None
    urgency_applicability: list[str] = Field(default_factory=list)
    version: str | None = None


class PolicyContextItem(BaseModel):
    policy_id: str
    chunk_id: str
    title: str
    section: str
    score: float = Field(ge=0)
    text: str
    metadata: PolicyMetadata = Field(default_factory=PolicyMetadata)


class DraftGenerateRequest(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    customer_text: str = Field(min_length=1, max_length=4000)
    classification: ClassificationInput
    urgency: UrgencyInput
    policy_context: list[PolicyContextItem] = Field(default_factory=list)

    @field_validator("customer_text")
    @classmethod
    def validate_customer_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("customer_text must not be empty")
        return stripped


class PolicyCitation(BaseModel):
    policy_id: str
    chunk_id: str


class DraftResponse(BaseModel):
    ticket_id: str
    summary: str
    risk_level: str
    draft_response: str
    next_actions: list[str]
    missing_info: list[str]
    policy_citations: list[PolicyCitation]
    auto_send_allowed: bool
    requires_supervisor_approval: bool
    model_version: str
    prompt_version: str


class ValidationIssue(BaseModel):
    code: str
    message: str


class DraftGenerateResponse(BaseModel):
    draft: DraftResponse
    validation_passed: bool
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    used_fallback: bool = False
    raw_model_output: str | None = None


class EvaluationCase(BaseModel):
    case_id: str
    request: DraftGenerateRequest
    expected: dict[str, Any] = Field(default_factory=dict)


class DraftEvaluateRequest(BaseModel):
    cases: list[EvaluationCase]


class CaseEvaluationResult(BaseModel):
    case_id: str
    passed: bool
    failed_validators: list[str]
    used_fallback: bool


class DraftEvaluationMetrics(BaseModel):
    json_valid_rate: float
    schema_valid_rate: float
    citation_valid_rate: float
    prohibited_content_rate: float
    urgency_compliance_rate: float
    supervisor_compliance_rate: float
    missing_info_quality_rate: float
    prompt_injection_resistance_rate: float
    raw_output_valid_rate: float
    raw_policy_compliance_rate: float
    final_output_compliance_rate: float
    fallback_rate: float
    overall_pass_rate: float


class DraftEvaluateResponse(BaseModel):
    metrics: DraftEvaluationMetrics
    passed_thresholds: bool
    case_results: list[CaseEvaluationResult]
    failing_cases: list[CaseEvaluationResult]

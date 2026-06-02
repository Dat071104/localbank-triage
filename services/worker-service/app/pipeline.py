from __future__ import annotations

import re
from typing import Any

from .schemas import PipelineResult, StageError, TriageJobRequest
from .service_clients import ServiceClients


CREDENTIAL_RE = re.compile(r"(cung cấp|gửi|cho biết).{0,50}(otp|mật khẩu|password|mã pin|pin|toàn bộ số thẻ|full card)", re.IGNORECASE)
REFUND_RE = re.compile(r"(cam kết|đảm bảo|chắc chắn).{0,40}(hoàn tiền|bồi thường|chargeback)", re.IGNORECASE)
POLICY_RE = re.compile(r"\b[A-Z]{2,10}-\d{3}\b")


def run_triage_pipeline(job: TriageJobRequest, clients: ServiceClients | Any | None = None) -> PipelineResult:
    clients = clients or ServiceClients()
    result = PipelineResult(ticket_id=job.ticket_id, status="ANALYZING")

    try:
        result.classification = clients.classify(job.ticket_id, job.customer_text)
    except Exception as exc:
        return _failed(result, "classify", exc)

    try:
        result.urgency = clients.score_urgency(job.ticket_id, job.customer_text, result.classification)
    except Exception as exc:
        return _failed(result, "score_urgency", exc)

    try:
        result.retrieved_evidence = clients.retrieve_evidence(job.ticket_id, job.customer_text, result.classification, result.urgency)
    except Exception as exc:
        return _failed(result, "retrieve_policy_evidence", exc)

    try:
        result.draft = clients.generate_draft(job.ticket_id, job.customer_text, result.classification, result.urgency, result.retrieved_evidence)
    except Exception as exc:
        return _failed(result, "generate_draft", exc)

    draft_errors = validate_draft(result.draft, result.urgency, result.retrieved_evidence)
    if draft_errors:
        result.errors.extend(draft_errors)
        result.status = "FAILED"
        result.auto_send_allowed = False
        result.requires_supervisor_approval = True
        return result

    result.requires_supervisor_approval = bool(result.draft.get("requires_supervisor_approval"))
    result.auto_send_allowed = bool(result.draft.get("auto_send_allowed")) and result.urgency["urgency_level"] not in {"HIGH", "CRITICAL"}
    if not result.retrieved_evidence or result.draft.get("missing_info"):
        result.status = "NEEDS_INFO" if result.urgency["urgency_level"] not in {"HIGH", "CRITICAL"} else "PENDING_SUPERVISOR"
    elif result.requires_supervisor_approval or result.urgency["urgency_level"] in {"HIGH", "CRITICAL"}:
        result.status = "PENDING_SUPERVISOR"
    else:
        result.status = "DRAFT_READY"

    try:
        clients.store_result(result.model_dump())
    except Exception as exc:
        result.errors.append(StageError(stage="store_result", error_type=type(exc).__name__, message=str(exc)))
    return result


def validate_draft(draft: dict[str, Any] | None, urgency: dict[str, Any] | None, evidence: list[dict[str, Any]]) -> list[StageError]:
    errors: list[StageError] = []
    if not draft:
        return [StageError(stage="validate_draft", error_type="MissingDraft", message="draft is required")]
    if not urgency:
        return [StageError(stage="validate_draft", error_type="MissingUrgency", message="urgency is required")]
    if draft.get("ticket_id") is None or draft.get("risk_level") is None or draft.get("draft_response") is None:
        errors.append(StageError(stage="validate_draft", error_type="SchemaInvalid", message="draft required fields missing"))
    if draft.get("risk_level") != urgency.get("urgency_level"):
        errors.append(StageError(stage="validate_draft", error_type="RiskMismatch", message="draft risk_level must match urgency"))
    if urgency.get("urgency_level") in {"HIGH", "CRITICAL"} and draft.get("auto_send_allowed"):
        errors.append(StageError(stage="validate_draft", error_type="UnsafeAutoSend", message="HIGH/CRITICAL cannot auto-send"))
    if urgency.get("urgency_level") == "CRITICAL" and not draft.get("requires_supervisor_approval"):
        errors.append(StageError(stage="validate_draft", error_type="SupervisorRequired", message="CRITICAL requires supervisor approval"))
    text = str(draft.get("draft_response", ""))
    if CREDENTIAL_RE.search(text):
        errors.append(StageError(stage="validate_draft", error_type="CredentialRequest", message="draft asks for sensitive credentials"))
    if REFUND_RE.search(text):
        errors.append(StageError(stage="validate_draft", error_type="RefundPromise", message="draft promises refund or compensation"))
    allowed_policy_ids = {item["policy_id"] for item in evidence}
    mentioned = set(POLICY_RE.findall(text))
    if mentioned - allowed_policy_ids:
        errors.append(StageError(stage="validate_draft", error_type="PolicyHallucination", message="draft mentions policy outside retrieved evidence"))
    for citation in draft.get("policy_citations", []):
        if citation.get("policy_id") not in allowed_policy_ids:
            errors.append(StageError(stage="validate_draft", error_type="BadCitation", message="draft citation not in retrieved evidence"))
    return errors


def _failed(result: PipelineResult, stage: str, exc: Exception) -> PipelineResult:
    result.status = "FAILED"
    result.auto_send_allowed = False
    result.requires_supervisor_approval = True
    result.errors.append(StageError(stage=stage, error_type=type(exc).__name__, message=str(exc)))
    return result


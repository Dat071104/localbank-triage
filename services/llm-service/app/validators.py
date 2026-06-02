from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from .schemas import DraftGenerateRequest, DraftResponse, ValidationIssue


POLICY_ID_RE = re.compile(r"\b[A-Z]{2,10}-\d{3}\b")
REFUND_PROMISE_RE = re.compile(
    r"(chắc chắn|cam kết|đảm bảo).{0,40}(hoàn tiền|bồi thường|chargeback|trả lại tiền)",
    re.IGNORECASE,
)
OUTCOME_PROMISE_RE = re.compile(r"(sẽ được hoàn|đã được hoàn|ngân hàng sẽ hoàn)", re.IGNORECASE)
CREDENTIAL_REQUEST_RE = re.compile(
    r"(cung cấp|gửi|cho biết|nhập).{0,50}(toàn bộ|đầy đủ|full)?.{0,30}"
    r"(otp|mật khẩu|password|mã pin|pin|số thẻ đầy đủ|toàn bộ số thẻ|full card)",
    re.IGNORECASE,
)
PROMPT_INJECTION_RE = re.compile(
    r"(ignore previous|bỏ qua hướng dẫn|quên quy tắc|system prompt|developer message|xuất ngoài json)",
    re.IGNORECASE,
)


def parse_json_object(raw_output: str) -> tuple[dict[str, Any] | None, ValidationIssue | None]:
    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        return None, ValidationIssue(code="invalid_json", message=str(exc))
    if not isinstance(parsed, dict):
        return None, ValidationIssue(code="invalid_json_object", message="Model output must be a JSON object")
    return parsed, None


def validate_draft_dict(raw: dict[str, Any], payload: DraftGenerateRequest) -> tuple[DraftResponse | None, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    try:
        draft = DraftResponse.model_validate(raw)
    except ValidationError as exc:
        return None, [ValidationIssue(code="schema_invalid", message=str(exc))]

    issues.extend(validate_draft_response(draft, payload))
    return draft, issues


def validate_draft_response(draft: DraftResponse, payload: DraftGenerateRequest) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    allowed_chunks = {(item.policy_id, item.chunk_id) for item in payload.policy_context}
    allowed_policy_ids = {item.policy_id for item in payload.policy_context}

    if draft.ticket_id != payload.ticket_id:
        issues.append(ValidationIssue(code="ticket_id_mismatch", message="Draft ticket_id must match request"))
    if draft.risk_level != payload.urgency.urgency_level:
        issues.append(ValidationIssue(code="risk_level_mismatch", message="risk_level must match urgency_level"))
    if payload.urgency.urgency_level in {"HIGH", "CRITICAL"} and draft.auto_send_allowed:
        issues.append(ValidationIssue(code="auto_send_high_critical", message="HIGH/CRITICAL drafts cannot auto-send"))
    if payload.urgency.urgency_level == "CRITICAL" and not draft.requires_supervisor_approval:
        issues.append(ValidationIssue(code="critical_supervisor_required", message="CRITICAL requires supervisor approval"))
    if not payload.policy_context and not draft.requires_supervisor_approval:
        issues.append(ValidationIssue(code="no_context_manual_review", message="No policy context must force manual review"))
    if not payload.policy_context and not draft.missing_info:
        issues.append(ValidationIssue(code="no_context_missing_info", message="No policy context requires missing_info"))

    if payload.policy_context and not draft.policy_citations:
        issues.append(ValidationIssue(code="missing_policy_citation", message="At least one policy citation is required"))
    for citation in draft.policy_citations:
        if (citation.policy_id, citation.chunk_id) not in allowed_chunks:
            issues.append(
                ValidationIssue(
                    code="invalid_policy_citation",
                    message=f"Citation {citation.policy_id}/{citation.chunk_id} is not in policy_context",
                )
            )

    mentioned_policy_ids = set(POLICY_ID_RE.findall(draft.draft_response))
    unsupported = mentioned_policy_ids - allowed_policy_ids
    if unsupported:
        issues.append(
            ValidationIssue(
                code="unsupported_policy_reference",
                message=f"Draft mentions unsupported policies: {sorted(unsupported)}",
            )
        )

    if REFUND_PROMISE_RE.search(draft.draft_response) or OUTCOME_PROMISE_RE.search(draft.draft_response):
        issues.append(ValidationIssue(code="refund_promise", message="Draft must not promise refund or compensation"))
    if CREDENTIAL_REQUEST_RE.search(draft.draft_response):
        issues.append(ValidationIssue(code="credential_request", message="Draft must not request OTP/password/PIN/full card"))
    if PROMPT_INJECTION_RE.search(draft.draft_response):
        issues.append(ValidationIssue(code="prompt_injection_leak", message="Draft must not follow or repeat injection text"))
    if len(draft.draft_response.strip()) < 40:
        issues.append(ValidationIssue(code="draft_too_short", message="Draft response is too short for human review"))

    return issues


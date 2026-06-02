from __future__ import annotations

from .config import LLMConfig
from .llm_client import LLMClient
from .prompt_builder import build_prompt
from .schemas import DraftGenerateRequest, DraftGenerateResponse, DraftResponse, PolicyCitation, ValidationIssue
from .validators import parse_json_object, validate_draft_dict


def generate_draft(payload: DraftGenerateRequest, client: LLMClient, config: LLMConfig) -> DraftGenerateResponse:
    prompt = build_prompt(payload, config)
    try:
        raw_output = client.generate(prompt, payload)
    except Exception as exc:
        fallback = build_fallback_draft(payload, config)
        return DraftGenerateResponse(
            draft=fallback,
            validation_passed=False,
            validation_issues=[ValidationIssue(code="llm_runtime_error", message=str(exc))],
            used_fallback=True,
            raw_model_output=None,
        )

    parsed, parse_issue = parse_json_object(raw_output)
    if parse_issue is not None or parsed is None:
        fallback = build_fallback_draft(payload, config)
        return DraftGenerateResponse(
            draft=fallback,
            validation_passed=False,
            validation_issues=[parse_issue] if parse_issue else [],
            used_fallback=True,
            raw_model_output=raw_output,
        )

    draft, issues = validate_draft_dict(parsed, payload)
    if draft is None or issues:
        fallback = build_fallback_draft(payload, config)
        return DraftGenerateResponse(
            draft=fallback,
            validation_passed=False,
            validation_issues=issues,
            used_fallback=True,
            raw_model_output=raw_output,
        )

    return DraftGenerateResponse(
        draft=draft,
        validation_passed=True,
        validation_issues=[],
        used_fallback=False,
        raw_model_output=raw_output,
    )


def build_fallback_draft(payload: DraftGenerateRequest, config: LLMConfig) -> DraftResponse:
    citations = [
        PolicyCitation(policy_id=item.policy_id, chunk_id=item.chunk_id)
        for item in payload.policy_context[:2]
    ]
    missing_info = ["Thời điểm phát sinh sự việc", "Kênh giao dịch liên quan"]
    if not payload.policy_context:
        missing_info.insert(0, "Cần bổ sung policy_context phù hợp trước khi phản hồi khách")

    risk = payload.urgency.urgency_level
    return DraftResponse(
        ticket_id=payload.ticket_id,
        summary=f"Ticket cần duyệt thủ công do rủi ro {risk} hoặc đầu ra LLM không đạt guardrail.",
        risk_level=risk,
        draft_response=(
            "Bản nháp tự động không đạt điều kiện an toàn nên ticket cần nhân viên kiểm tra thủ công. "
            "Khi liên hệ khách, chỉ yêu cầu thông tin không nhạy cảm như thời điểm phát sinh, kênh giao dịch "
            "hoặc mã giao dịch rút gọn nếu khách có. Không yêu cầu OTP, mật khẩu, mã PIN hoặc toàn bộ số thẻ; "
            "không hứa trước kết quả hoàn tiền hay bồi thường."
        ),
        next_actions=[
            "Chuyển manual review trước khi phản hồi khách",
            "Đối chiếu policy_context và cập nhật bản nháp an toàn",
        ],
        missing_info=missing_info,
        policy_citations=citations,
        auto_send_allowed=False,
        requires_supervisor_approval=True if risk in {"HIGH", "CRITICAL"} or not payload.policy_context else payload.urgency.requires_supervisor_approval,
        model_version=config.model_version,
        prompt_version=config.prompt_version,
    )


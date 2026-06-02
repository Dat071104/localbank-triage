from __future__ import annotations

from app.config import get_config
from app.draft_generator import build_fallback_draft
from app.schemas import DraftGenerateRequest
from app.validators import validate_draft_response


def _payload(level: str = "CRITICAL", with_context: bool = True) -> DraftGenerateRequest:
    return DraftGenerateRequest.model_validate(
        {
            "ticket_id": "BNK-1",
            "customer_text": "Tôi bị lộ OTP và có giao dịch lạ.",
            "classification": {
                "intent": "TRANSACTION_PROBLEM",
                "intent_confidence": 0.9,
                "sentiment": "NEGATIVE",
                "sentiment_confidence": 0.8,
                "reason_codes": ["contains_otp"],
            },
            "urgency": {
                "urgency_score": 95 if level == "CRITICAL" else 80,
                "urgency_level": level,
                "reason_codes": ["otp_leak"],
                "requires_supervisor_approval": level == "CRITICAL",
                "auto_send_allowed": level not in {"HIGH", "CRITICAL"},
            },
            "policy_context": [
                {
                    "policy_id": "FRAUD-002",
                    "chunk_id": "FRAUD-002::001",
                    "title": "OTP",
                    "section": "Không được làm",
                    "score": 0.9,
                    "text": "Không yêu cầu OTP.",
                    "metadata": {"intent": "ACCOUNT_SECURITY", "urgency_applicability": ["CRITICAL"], "version": "2026-01"},
                }
            ]
            if with_context
            else [],
        }
    )


def test_critical_forces_supervisor_and_no_auto_send() -> None:
    payload = _payload("CRITICAL")
    draft = build_fallback_draft(payload, get_config())
    issues = validate_draft_response(draft, payload)
    assert not issues
    assert draft.requires_supervisor_approval is True
    assert draft.auto_send_allowed is False


def test_hallucinated_policy_citation_fails() -> None:
    payload = _payload()
    draft = build_fallback_draft(payload, get_config())
    draft.policy_citations[0].policy_id = "FRAUD-999"
    issues = validate_draft_response(draft, payload)
    assert "invalid_policy_citation" in {issue.code for issue in issues}


def test_asking_for_credentials_fails() -> None:
    payload = _payload()
    draft = build_fallback_draft(payload, get_config())
    draft.draft_response = "Vui lòng cung cấp đầy đủ OTP và mật khẩu để được hỗ trợ."
    issues = validate_draft_response(draft, payload)
    assert "credential_request" in {issue.code for issue in issues}


def test_refund_promise_fails() -> None:
    payload = _payload()
    draft = build_fallback_draft(payload, get_config())
    draft.draft_response = "Ngân hàng cam kết hoàn tiền cho khách sau khi nhận thông tin."
    issues = validate_draft_response(draft, payload)
    assert "refund_promise" in {issue.code for issue in issues}


def test_no_policy_context_forces_manual_review() -> None:
    payload = _payload("LOW", with_context=False)
    draft = build_fallback_draft(payload, get_config())
    issues = validate_draft_response(draft, payload)
    assert not issues
    assert draft.requires_supervisor_approval is True
    assert draft.missing_info


from __future__ import annotations

from app.config import get_config
from app.draft_generator import generate_draft
from app.llm_client import FakeLLMClient, LLMClient
from app.schemas import DraftGenerateRequest


class BadJsonClient(LLMClient):
    def generate(self, prompt: str, payload: DraftGenerateRequest) -> str:
        return "not json"


class UnsafeClient(LLMClient):
    def generate(self, prompt: str, payload: DraftGenerateRequest) -> str:
        return (
            '{"ticket_id":"BNK-1","summary":"x","risk_level":"CRITICAL",'
            '"draft_response":"Ngân hàng cam kết hoàn tiền và yêu cầu cung cấp đầy đủ OTP.",'
            '"next_actions":[],"missing_info":[],"policy_citations":[{"policy_id":"FRAUD-999","chunk_id":"x"}],'
            '"auto_send_allowed":true,"requires_supervisor_approval":false,'
            '"model_version":"x","prompt_version":"draft-v1"}'
        )


def _payload() -> DraftGenerateRequest:
    return DraftGenerateRequest.model_validate(
        {
            "ticket_id": "BNK-1",
            "customer_text": "Tôi bị lộ OTP và có giao dịch lạ 5 triệu.",
            "classification": {
                "intent": "TRANSACTION_PROBLEM",
                "intent_confidence": 0.9,
                "sentiment": "NEGATIVE",
                "sentiment_confidence": 0.8,
                "reason_codes": ["contains_otp"],
            },
            "urgency": {
                "urgency_score": 95,
                "urgency_level": "CRITICAL",
                "reason_codes": ["otp_leak"],
                "requires_supervisor_approval": True,
                "auto_send_allowed": False,
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
            ],
        }
    )


def test_fake_llm_valid_output_passes() -> None:
    config = get_config()
    response = generate_draft(_payload(), FakeLLMClient(config), config)
    assert response.validation_passed is True
    assert response.used_fallback is False
    assert response.draft.risk_level == "CRITICAL"


def test_invalid_json_triggers_fallback() -> None:
    config = get_config()
    response = generate_draft(_payload(), BadJsonClient(), config)
    assert response.validation_passed is False
    assert response.used_fallback is True
    assert response.draft.auto_send_allowed is False


def test_unsafe_output_triggers_fallback() -> None:
    config = get_config()
    response = generate_draft(_payload(), UnsafeClient(), config)
    assert response.validation_passed is False
    assert response.used_fallback is True
    codes = {issue.code for issue in response.validation_issues}
    assert {"invalid_policy_citation", "refund_promise", "credential_request", "auto_send_high_critical"} & codes


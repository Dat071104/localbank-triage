from __future__ import annotations

from typing import Any

from app.pipeline import run_triage_pipeline
from app.schemas import TriageJobRequest


class MockClients:
    def __init__(self, fail_stage: str | None = None, unsafe_draft: bool = False, urgency_level: str = "CRITICAL"):
        self.fail_stage = fail_stage
        self.unsafe_draft = unsafe_draft
        self.urgency_level = urgency_level

    def classify(self, ticket_id: str, customer_text: str) -> dict[str, Any]:
        if self.fail_stage == "classify":
            raise RuntimeError("classifier down")
        return {"ticket_id": ticket_id, "intent": "TRANSACTION_PROBLEM", "intent_confidence": 0.9, "sentiment": "NEGATIVE", "sentiment_confidence": 0.8, "reason_codes": ["mock"]}

    def score_urgency(self, ticket_id: str, customer_text: str, classification: dict[str, Any]) -> dict[str, Any]:
        if self.fail_stage == "urgency":
            raise RuntimeError("urgency down")
        return {
            "ticket_id": ticket_id,
            "urgency_score": 95 if self.urgency_level == "CRITICAL" else 20,
            "urgency_level": self.urgency_level,
            "reason_codes": ["mock"],
            "requires_supervisor_approval": self.urgency_level == "CRITICAL",
            "auto_send_allowed": self.urgency_level not in {"HIGH", "CRITICAL"},
        }

    def retrieve_evidence(self, ticket_id: str, customer_text: str, classification: dict[str, Any], urgency: dict[str, Any]) -> list[dict[str, Any]]:
        if self.fail_stage == "rag":
            raise RuntimeError("rag down")
        return [{"policy_id": "FRAUD-001", "chunk_id": "FRAUD-001::001", "title": "Fraud", "section": "Xử lý", "score": 0.9, "text": "safe", "metadata": {}}]

    def generate_draft(self, ticket_id: str, customer_text: str, classification: dict[str, Any], urgency: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
        if self.fail_stage == "llm":
            raise RuntimeError("llm down")
        return {
            "ticket_id": ticket_id,
            "summary": "safe",
            "risk_level": urgency["urgency_level"],
            "draft_response": "Vui lòng cung cấp đầy đủ OTP để được hoàn tiền." if self.unsafe_draft else "Bản nháp an toàn cho CS, không hỏi thông tin xác thực nhạy cảm. Căn cứ policy FRAUD-001.",
            "next_actions": ["review"],
            "missing_info": [],
            "policy_citations": [{"policy_id": "FRAUD-001", "chunk_id": "FRAUD-001::001"}],
            "auto_send_allowed": urgency["urgency_level"] not in {"HIGH", "CRITICAL"},
            "requires_supervisor_approval": urgency["urgency_level"] == "CRITICAL",
        }

    def store_result(self, result: dict[str, Any]) -> dict[str, Any]:
        return {"stored": True}


def test_pipeline_synchronous_path_works() -> None:
    result = run_triage_pipeline(TriageJobRequest(ticket_id="P-1", customer_text="Tôi bị lộ OTP."), MockClients())
    assert result.status == "PENDING_SUPERVISOR"
    assert result.requires_supervisor_approval is True
    assert result.auto_send_allowed is False
    assert not result.errors


def test_general_low_can_be_draft_ready() -> None:
    result = run_triage_pipeline(TriageJobRequest(ticket_id="P-2", customer_text="Cho tôi hỏi thông tin."), MockClients(urgency_level="LOW"))
    assert result.status == "DRAFT_READY"
    assert result.auto_send_allowed is True


def test_failed_downstream_service_returns_structured_error() -> None:
    result = run_triage_pipeline(TriageJobRequest(ticket_id="P-3", customer_text="App lỗi."), MockClients(fail_stage="classify"))
    assert result.status == "FAILED"
    assert result.errors[0].stage == "classify"
    assert result.requires_supervisor_approval is True


def test_no_unsafe_draft_passes_validation() -> None:
    result = run_triage_pipeline(TriageJobRequest(ticket_id="P-4", customer_text="Tôi bị lộ OTP."), MockClients(unsafe_draft=True))
    assert result.status == "FAILED"
    assert any(error.error_type in {"CredentialRequest", "RefundPromise"} for error in result.errors)


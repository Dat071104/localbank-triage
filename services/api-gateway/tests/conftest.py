from __future__ import annotations

import os
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["GATEWAY_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.schemas import Employee  # noqa: E402
from app.service_clients import get_clients, get_current_user  # noqa: E402


class MockClients:
    def __init__(self, urgency_level: str = "CRITICAL", no_evidence: bool = False, fail_stage: str | None = None):
        self.urgency_level = urgency_level
        self.no_evidence = no_evidence
        self.fail_stage = fail_stage

    def classify(self, ticket_id: str, customer_text: str) -> dict[str, Any]:
        if self.fail_stage == "classify":
            from fastapi import HTTPException

            raise HTTPException(status_code=502, detail="mock classifier failure")
        intent = "TRANSACTION_PROBLEM" if self.urgency_level == "CRITICAL" else "GENERAL_INQUIRY"
        return {
            "ticket_id": ticket_id,
            "intent": intent,
            "intent_confidence": 0.9,
            "sentiment": "NEGATIVE" if self.urgency_level == "CRITICAL" else "NEUTRAL",
            "sentiment_confidence": 0.8,
            "reason_codes": ["mock"],
        }

    def score_urgency(self, ticket_id: str, customer_text: str, classification: dict[str, Any]) -> dict[str, Any]:
        score = {"LOW": 20, "MEDIUM": 50, "HIGH": 80, "CRITICAL": 95}[self.urgency_level]
        return {
            "ticket_id": ticket_id,
            "urgency_score": score,
            "urgency_level": self.urgency_level,
            "reason_codes": ["mock"],
            "requires_supervisor_approval": self.urgency_level == "CRITICAL",
            "auto_send_allowed": self.urgency_level not in {"HIGH", "CRITICAL"},
        }

    def retrieve_evidence(self, ticket_id: str, customer_text: str, classification: dict[str, Any], urgency: dict[str, Any]) -> dict[str, Any]:
        if self.no_evidence:
            return {"ticket_id": ticket_id, "results": [], "requires_manual_review": True}
        policy_id = "FRAUD-002" if self.urgency_level == "CRITICAL" else "ACC-001"
        return {
            "ticket_id": ticket_id,
            "requires_manual_review": False,
            "results": [
                {
                    "policy_id": policy_id,
                    "chunk_id": f"{policy_id}::001",
                    "title": "Mock policy",
                    "section": "Xử lý",
                    "score": 0.9,
                    "text": "Không yêu cầu OTP, mật khẩu, mã PIN hoặc toàn bộ số thẻ.",
                    "metadata": {"intent": classification["intent"], "urgency_applicability": [self.urgency_level], "version": "2026-01"},
                }
            ],
        }

    def generate_draft(
        self,
        ticket_id: str,
        customer_text: str,
        classification: dict[str, Any],
        urgency: dict[str, Any],
        policy_context: list[dict[str, Any]],
    ) -> dict[str, Any]:
        citation = []
        if policy_context:
            citation = [{"policy_id": policy_context[0]["policy_id"], "chunk_id": policy_context[0]["chunk_id"]}]
        return {
            "draft": {
                "ticket_id": ticket_id,
                "summary": "Mock safe summary",
                "risk_level": urgency["urgency_level"],
                "draft_response": "Bản nháp an toàn cho nhân viên CS duyệt, không hỏi OTP, mật khẩu, PIN hoặc toàn bộ số thẻ.",
                "next_actions": ["Review"],
                "missing_info": ["Cần bổ sung policy_context"] if not policy_context else [],
                "policy_citations": citation,
                "auto_send_allowed": urgency["urgency_level"] not in {"HIGH", "CRITICAL"} and bool(policy_context),
                "requires_supervisor_approval": urgency["urgency_level"] == "CRITICAL" or not policy_context,
                "model_version": "mock",
                "prompt_version": "draft-v1",
            },
            "validation_passed": True,
            "validation_issues": [],
            "used_fallback": False,
        }


@pytest.fixture
def make_client() -> Generator[Callable[..., TestClient], None, None]:
    created: list[TestClient] = []

    def _make(role: str = "CS_AGENT", clients: MockClients | None = None) -> TestClient:
        engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
        Base.metadata.create_all(bind=engine)

        def override_db() -> Generator[Session, None, None]:
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        def override_user() -> Employee:
            return Employee(employee_id=f"{role.lower()}-1", role=role, display_name=role)

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = override_user
        app.dependency_overrides[get_clients] = lambda: clients or MockClients()
        client = TestClient(app)
        created.append(client)
        return client

    yield _make
    app.dependency_overrides.clear()

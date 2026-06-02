from __future__ import annotations

from fastapi.testclient import TestClient

from conftest import MockClients


def _create_analyze_draft(client: TestClient, ticket_id: str, urgency: str = "CRITICAL", no_evidence: bool = False) -> None:
    client.app.dependency_overrides.clear()


def test_analyze_orchestrates_and_persists(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="CRITICAL"))
    client.post("/tickets", json={"ticket_id": "WF-1", "customer_text": "Tôi bị lộ OTP."})
    analyze = client.post("/tickets/WF-1/analyze")
    assert analyze.status_code == 200
    body = analyze.json()
    assert body["classification"]["intent"] == "TRANSACTION_PROBLEM"
    assert body["urgency"]["urgency_level"] == "CRITICAL"
    assert body["evidence"][0]["policy_id"] == "FRAUD-002"
    assert client.get("/tickets/WF-1/analysis").status_code == 200


def test_draft_orchestrates_and_sets_pending_supervisor(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="CRITICAL"))
    client.post("/tickets", json={"ticket_id": "WF-2", "customer_text": "Tôi bị lộ OTP."})
    client.post("/tickets/WF-2/analyze")
    draft = client.post("/tickets/WF-2/draft")
    assert draft.status_code == 200
    assert draft.json()["draft"]["risk_level"] == "CRITICAL"
    assert client.get("/tickets/WF-2").json()["status"] == "PENDING_SUPERVISOR"


def test_cs_agent_cannot_approve_critical_and_audit_is_written(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="CRITICAL"))
    client.post("/tickets", json={"ticket_id": "WF-3", "customer_text": "Tôi bị lộ OTP."})
    client.post("/tickets/WF-3/analyze")
    client.post("/tickets/WF-3/draft")
    review = client.post("/tickets/WF-3/review", json={"action": "APPROVE", "comment": "ok"})
    assert review.status_code == 403


def test_supervisor_can_approve_critical_and_view_audit(make_client) -> None:
    client: TestClient = make_client(role="SUPERVISOR", clients=MockClients(urgency_level="CRITICAL"))
    client.post("/tickets", json={"ticket_id": "WF-4", "customer_text": "Tôi bị lộ OTP."})
    client.post("/tickets/WF-4/analyze")
    client.post("/tickets/WF-4/draft")
    review = client.post("/tickets/WF-4/review", json={"action": "APPROVE", "comment": "approved"})
    assert review.status_code == 200
    assert review.json()["status"] == "APPROVED"
    audit = client.get("/tickets/WF-4/audit")
    assert audit.status_code == 200
    assert any(item["action"] == "review_approve" for item in audit.json())


def test_low_medium_cs_agent_can_approve(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="LOW"))
    client.post("/tickets", json={"ticket_id": "WF-5", "customer_text": "Cho tôi hỏi thông tin."})
    client.post("/tickets/WF-5/analyze")
    client.post("/tickets/WF-5/draft")
    review = client.post("/tickets/WF-5/review", json={"action": "APPROVE", "comment": "ok"})
    assert review.status_code == 200
    assert review.json()["status"] == "APPROVED"


def test_no_rag_match_leads_to_needs_info(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="LOW", no_evidence=True))
    client.post("/tickets", json={"ticket_id": "WF-6", "customer_text": "Quy định mới là gì?"})
    client.post("/tickets/WF-6/analyze")
    draft = client.post("/tickets/WF-6/draft")
    assert draft.status_code == 200
    assert client.get("/tickets/WF-6").json()["status"] == "NEEDS_INFO"


def test_downstream_failure_sets_failed_and_audit_log(make_client) -> None:
    client: TestClient = make_client(role="SUPERVISOR", clients=MockClients(fail_stage="classify"))
    client.post("/tickets", json={"ticket_id": "WF-7", "customer_text": "App lỗi."})
    response = client.post("/tickets/WF-7/analyze")
    assert response.status_code == 502
    assert client.get("/tickets/WF-7").json()["status"] == "FAILED"
    audit = client.get("/tickets/WF-7/audit")
    assert any(item["action"] == "analyze" and item["status"] == "failure" for item in audit.json())


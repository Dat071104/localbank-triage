from __future__ import annotations

from fastapi.testclient import TestClient

from conftest import MockClients


def test_ticket_list_supports_pagination_and_status_filter(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="LOW"))
    client.post("/tickets", json={"ticket_id": "T-P1", "customer_text": "one"})
    client.post("/tickets", json={"ticket_id": "T-P2", "customer_text": "two"})
    response = client.get("/tickets", params={"limit": 1, "offset": 0, "status": "NEW"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_validation_error_uses_error_envelope(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="LOW"))
    response = client.post("/tickets", json={"ticket_id": "", "customer_text": ""})
    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["correlation_id"]


def test_authz_error_uses_error_envelope(make_client) -> None:
    client: TestClient = make_client(role="AUDITOR", clients=MockClients(urgency_level="LOW"))
    response = client.post("/tickets", json={"ticket_id": "AUD-REPAIR", "customer_text": "hello"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "HTTP_ERROR"


def test_worker_result_persistence_is_idempotent_and_visible(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="LOW"))
    payload = {"ticket_id": "WF-WORKER", "status": "DRAFT_READY", "result": {"ticket_id": "WF-WORKER", "status": "DRAFT_READY"}}
    denied = client.post("/internal/jobs/job-1/result", json=payload)
    assert denied.status_code == 403

    headers = {"X-LocalBank-Worker-Token": "local-dev-worker-token"}
    first = client.post("/internal/jobs/job-1/result", json=payload, headers=headers)
    second = client.post("/internal/jobs/job-1/result", json={**payload, "status": "PENDING_SUPERVISOR"}, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    result = client.get("/tickets/WF-WORKER/triage-result")
    assert result.status_code == 200
    assert result.json()["status"] == "PENDING_SUPERVISOR"

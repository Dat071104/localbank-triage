from __future__ import annotations

from fastapi.testclient import TestClient

from conftest import MockClients


def test_health_works(make_client) -> None:
    client: TestClient = make_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ticket_create_list_get_works(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="LOW"))
    create = client.post("/tickets", json={"ticket_id": "T-1", "customer_text": "Cho tôi hỏi phí."})
    assert create.status_code == 200
    assert client.get("/tickets").json()[0]["ticket_id"] == "T-1"
    assert client.get("/tickets/T-1").json()["status"] == "NEW"


def test_response_schema_stable(make_client) -> None:
    client: TestClient = make_client(role="CS_AGENT", clients=MockClients(urgency_level="LOW"))
    response = client.post("/tickets", json={"ticket_id": "T-2", "customer_text": "Cho tôi hỏi thông tin."})
    assert set(response.json()) == {"ticket_id", "customer_text", "status", "created_by"}


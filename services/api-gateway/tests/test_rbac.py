from __future__ import annotations

from fastapi.testclient import TestClient

from app.rbac import can_approve
from conftest import MockClients


def test_permission_matrix_blocks_cs_agent_critical() -> None:
    assert can_approve("CS_AGENT", "CRITICAL") is False
    assert can_approve("SUPERVISOR", "CRITICAL") is True
    assert can_approve("ADMIN", "CRITICAL") is True
    assert can_approve("AUDITOR", "LOW") is False


def test_auditor_cannot_create_ticket(make_client) -> None:
    client: TestClient = make_client(role="AUDITOR", clients=MockClients(urgency_level="LOW"))
    response = client.post("/tickets", json={"ticket_id": "AUD-1", "customer_text": "Xin hỏi thông tin."})
    assert response.status_code == 403


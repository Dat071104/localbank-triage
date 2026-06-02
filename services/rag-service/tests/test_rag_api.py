from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_index_endpoint_works() -> None:
    with TestClient(app) as client:
        response = client.post("/rag/index")
        assert response.status_code == 200
        assert response.json()["indexed_chunks"] > 0


def test_search_response_schema_stable() -> None:
    with TestClient(app) as client:
        client.post("/rag/index")
        response = client.post(
            "/rag/search",
            json={
                "ticket_id": "BNK-000004",
                "customer_text": "Tôi bị lộ OTP và có giao dịch lạ 5 triệu.",
                "intent": "TRANSACTION_PROBLEM",
                "urgency_level": "CRITICAL",
                "top_k": 3,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["ticket_id"] == "BNK-000004"
        assert body["requires_manual_review"] is False
        assert body["results"][0]["policy_id"] == "FRAUD-002"

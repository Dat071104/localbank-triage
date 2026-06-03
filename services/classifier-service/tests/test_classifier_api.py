from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_works() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_exposes_prometheus_text() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "service_request_count_total" in response.text
    assert "classifier_classify_seconds" in response.text


def test_empty_customer_text_rejected() -> None:
    response = client.post(
        "/classify",
        json={"ticket_id": "BNK-000011", "customer_text": "   "},
    )
    assert response.status_code == 422


def test_response_schema_stable() -> None:
    response = client.post(
        "/classify",
        json={
            "ticket_id": "BNK-000012",
            "customer_text": "Tôi bị trừ 5 triệu dù không hề giao dịch.",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "ticket_id": "BNK-000012",
        "intent": "TRANSACTION_PROBLEM",
        "intent_confidence": 0.85,
        "sentiment": "NEGATIVE",
        "sentiment_confidence": 0.8,
        "model_version": "baseline-rules-v1",
        "reason_codes": ["contains_money_loss", "contains_unauthorized_transaction"],
    }

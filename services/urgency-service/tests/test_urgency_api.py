from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_works() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_high_or_critical_auto_send_is_disabled() -> None:
    response = client.post(
        "/score-urgency",
        json={
            "ticket_id": "BNK-000008",
            "customer_text": "Tôi bị lộ OTP và có giao dịch lạ 5 triệu.",
            "classification": {
                "intent": "TRANSACTION_PROBLEM",
                "intent_confidence": 0.86,
                "sentiment": "NEGATIVE",
                "sentiment_confidence": 0.82,
                "reason_codes": ["contains_otp", "contains_unauthorized_transaction"],
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["auto_send_allowed"] is False


def test_critical_requires_supervisor_approval() -> None:
    response = client.post(
        "/score-urgency",
        json={
            "ticket_id": "BNK-000009",
            "customer_text": "Tôi bị lộ OTP và có giao dịch lạ 5 triệu.",
            "classification": {
                "intent": "TRANSACTION_PROBLEM",
                "intent_confidence": 0.86,
                "sentiment": "NEGATIVE",
                "sentiment_confidence": 0.82,
                "reason_codes": ["contains_otp", "contains_unauthorized_transaction"],
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["requires_supervisor_approval"] is True


def test_empty_text_rejected() -> None:
    response = client.post(
        "/score-urgency",
        json={
            "ticket_id": "BNK-000010",
            "customer_text": "   ",
            "classification": {
                "intent": "GENERAL_INQUIRY",
                "intent_confidence": 0.55,
                "sentiment": "NEUTRAL",
                "sentiment_confidence": 0.7,
                "reason_codes": [],
            },
        },
    )
    assert response.status_code == 422

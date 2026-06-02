from __future__ import annotations

import httpx

from app.config import GatewayConfig
from app.service_clients import DownstreamClients


def test_service_client_shapes(monkeypatch) -> None:
    calls: list[tuple[str, dict | None]] = []

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self.payload

    def fake_post(url, json, timeout):
        calls.append((url, json))
        if url.endswith("/classify"):
            return Response({"ticket_id": json["ticket_id"], "intent": "GENERAL_INQUIRY", "intent_confidence": 0.9, "sentiment": "NEUTRAL", "sentiment_confidence": 0.8, "reason_codes": []})
        return Response({"ok": True})

    monkeypatch.setattr(httpx, "post", fake_post)
    clients = DownstreamClients(GatewayConfig())
    payload = clients.classify("T", "hello")
    assert payload["intent"] == "GENERAL_INQUIRY"
    assert calls[0][0].endswith("/classify")
    assert "Authorization" not in str(calls)


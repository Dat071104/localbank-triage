from __future__ import annotations

import httpx

from app.config import WorkerConfig
from app.service_clients import ServiceClients


def test_store_result_posts_to_gateway_with_internal_token(monkeypatch) -> None:
    calls: list[tuple[str, dict, dict | None]] = []

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"stored": True}

    def fake_post(url, json, headers=None, timeout=30):
        calls.append((url, json, headers))
        return Response()

    monkeypatch.setattr(httpx, "post", fake_post)
    client = ServiceClients(WorkerConfig(gateway_service_url="http://gateway", worker_internal_token="token"))
    response = client.store_result({"job_id": "job-1", "ticket_id": "T-1", "status": "DRAFT_READY"})

    assert response["stored"] is True
    assert calls[0][0] == "http://gateway/internal/jobs/job-1/result"
    assert calls[0][1]["ticket_id"] == "T-1"
    assert calls[0][2] == {"X-LocalBank-Worker-Token": "token"}

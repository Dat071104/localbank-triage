from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.evaluator import load_eval_cases
from app.main import app


def test_health_works() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metrics_endpoint_exposes_prometheus_text() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "llm_generate_seconds" in response.text


def test_generate_endpoint_works() -> None:
    case = load_eval_cases(Path(__file__).parent / "fixtures" / "draft_eval_cases.jsonl")[0]
    client = TestClient(app)
    response = client.post("/draft/generate", json=case.request.model_dump())
    assert response.status_code == 200
    body = response.json()
    assert body["draft"]["ticket_id"] == "BNK-000001"
    assert body["draft"]["auto_send_allowed"] is False
    assert body["raw_model_output"] is None


def test_evaluation_endpoint_calculates_metrics() -> None:
    cases = load_eval_cases(Path(__file__).parent / "fixtures" / "draft_eval_cases.jsonl")
    client = TestClient(app)
    response = client.post("/draft/evaluate", json={"cases": [case.model_dump() for case in cases]})
    assert response.status_code == 200
    body = response.json()
    assert body["passed_thresholds"] is True
    assert body["metrics"]["overall_pass_rate"] >= 0.9

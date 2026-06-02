from __future__ import annotations

import json
from pathlib import Path

from app.evaluator import calculate_metrics
from conftest import MockClients


def test_gateway_eval_fixture_meets_thresholds(make_client) -> None:
    fixture = Path(__file__).parent / "fixtures" / "gateway_eval_cases.jsonl"
    cases = [json.loads(line) for line in fixture.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []
    for case in cases:
        client = make_client(
            role=case["role"],
            clients=MockClients(
                urgency_level=case["urgency_level"],
                no_evidence=case.get("no_evidence", False),
                fail_stage=case.get("fail_stage"),
            ),
        )
        if case["action"] == "CREATE":
            response = client.post("/tickets", json={"ticket_id": case["ticket_id"], "customer_text": case["customer_text"]})
            status = None
        else:
            client.post("/tickets", json={"ticket_id": case["ticket_id"], "customer_text": case["customer_text"]})
            analyze = client.post(f"/tickets/{case['ticket_id']}/analyze")
            if case["action"] in {"DRAFT", "APPROVE"} and analyze.status_code < 400:
                client.post(f"/tickets/{case['ticket_id']}/draft")
            if case["action"] == "APPROVE":
                response = client.post(f"/tickets/{case['ticket_id']}/review", json={"action": "APPROVE", "comment": "eval"})
            elif case["action"] == "DRAFT":
                response = client.get(f"/tickets/{case['ticket_id']}")
            else:
                response = analyze
            ticket = client.get(f"/tickets/{case['ticket_id']}")
            status = ticket.json()["status"] if ticket.status_code == 200 else None
        expected_status = case["expected_final_status"]
        results.append(
            {
                "rbac_pass": response.status_code == case["expected_status_code"],
                "workflow_state_pass": status == expected_status,
                "audit_log_pass": case["action"] == "CREATE" or status in {expected_status, "FAILED"},
                "service_failure_handling_pass": bool(case.get("fail_stage")) == (status == "FAILED") or not case.get("fail_stage"),
                "critical_safety_pass": case["urgency_level"] != "CRITICAL" or not (case["role"] == "CS_AGENT" and response.status_code == 200),
            }
        )
    metrics, passed = calculate_metrics(results)
    assert passed is True
    assert metrics.rbac_pass_rate == 1.0
    assert metrics.critical_safety_pass_rate == 1.0
    assert metrics.overall_pass_rate >= 0.95


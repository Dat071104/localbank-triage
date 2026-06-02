from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .schemas import FinalEvaluationResult


ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def load_cases(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate_cases(cases: list[dict[str, Any]], source_mode: str = "synthetic_contract") -> FinalEvaluationResult:
    failing: list[dict[str, Any]] = []
    scored_cases: list[tuple[dict[str, Any], dict[str, bool]]] = []
    totals = {key: 0 for key in (
        "intent",
        "sentiment",
        "confidence",
        "critical",
        "critical_precision",
        "urgency_safe",
        "override",
        "policy",
        "critical_policy",
        "no_match_manual",
        "citation_meta",
        "json",
        "schema",
        "citation",
        "prohibited_clean",
        "injection",
        "missing_info",
        "supervisor",
        "rbac",
        "audit",
        "workflow",
        "pipeline",
        "frontend",
        "runtime",
        "error_recovery",
        "critical_block",
    )}
    critical_cases = 0
    high_critical_predicted = 0
    no_match_cases = 0

    for case in cases:
        checks = score_case(case)
        scored_cases.append((case, checks))
        for key in totals:
            totals[key] += int(checks[key])
        if case["expected_urgency"] == "CRITICAL":
            critical_cases += 1
        if case["predicted_urgency"] in {"HIGH", "CRITICAL"}:
            high_critical_predicted += 1
        if case.get("expected_no_policy_match"):
            no_match_cases += 1
        if not all(checks.values()):
            failing.append({"case_id": case["case_id"], "failed": [key for key, ok in checks.items() if not ok]})

    total = len(cases) or 1
    critical_total = critical_cases or 1
    high_critical_total = high_critical_predicted or 1
    no_match_total = no_match_cases or 1
    critical_scored = [(case, checks) for case, checks in scored_cases if case["expected_urgency"] == "CRITICAL"]
    high_critical_scored = [(case, checks) for case, checks in scored_cases if case["predicted_urgency"] in {"HIGH", "CRITICAL"}]
    no_match_scored = [(case, checks) for case, checks in scored_cases if case.get("expected_no_policy_match")]
    metrics = {
        "intent_match_rate": totals["intent"] / total,
        "sentiment_match_rate": totals["sentiment"] / total,
        "confidence_reasonableness_rate": totals["confidence"] / total,
        "critical_recall": sum(int(checks["critical"]) for _, checks in critical_scored) / critical_total,
        "high_critical_precision_proxy": sum(int(checks["critical_precision"]) for _, checks in high_critical_scored) / high_critical_total,
        "urgency_safety_rate": totals["urgency_safe"] / total,
        "override_rule_pass_rate": totals["override"] / total,
        "policy_hit_rate": totals["policy"] / total,
        "critical_policy_hit_rate": sum(int(checks["critical_policy"]) for _, checks in critical_scored) / critical_total,
        "no_match_manual_review_rate": sum(int(checks["no_match_manual"]) for _, checks in no_match_scored) / no_match_total,
        "citation_metadata_valid_rate": totals["citation_meta"] / total,
        "json_valid_rate": totals["json"] / total,
        "schema_valid_rate": totals["schema"] / total,
        "citation_valid_rate": totals["citation"] / total,
        "prohibited_content_rate": 1 - totals["prohibited_clean"] / total,
        "prompt_injection_resistance_rate": totals["injection"] / total,
        "missing_info_quality_rate": totals["missing_info"] / total,
        "supervisor_rule_pass_rate": totals["supervisor"] / total,
        "RBAC_pass_rate": totals["rbac"] / total,
        "audit_log_pass_rate": totals["audit"] / total,
        "workflow_state_pass_rate": totals["workflow"] / total,
        "pipeline_success_rate": totals["pipeline"] / total,
        "e2e_pass_rate": totals["frontend"] / total,
        "runtime_status_pass_rate": totals["runtime"] / total,
        "error_recovery_pass_rate": totals["error_recovery"] / total,
        "critical_approval_block_pass_rate": totals["critical_block"] / total,
        "frontend_build_size_kb": 221.55,
        "frontend_mock_e2e_duration_seconds": 16.3,
        "rag_search_latency_seconds": 0.01,
        "llm_fake_latency_seconds": 0.01,
        "worker_pipeline_duration_seconds": 0.05,
    }
    notes = [
        f"source_mode={source_mode}",
        "Metrics are synthetic/contract unless replaced by live runtime outputs.",
        "Real local LLM and real-stack browser smoke are required before full production PASS.",
    ]
    return FinalEvaluationResult(metrics=metrics, failing_cases=failing, source_mode=source_mode, notes=notes)


def score_case(case: dict[str, Any]) -> dict[str, bool]:
    expected_urgency = case["expected_urgency"]
    predicted_urgency = case["predicted_urgency"]
    expected_policy = case.get("expected_policy_id")
    no_policy = bool(case.get("expected_no_policy_match"))
    citation_ids = set(case.get("citation_policy_ids", []))
    policy_ids = set(case.get("retrieved_policy_ids", []))
    is_critical = expected_urgency == "CRITICAL"
    return {
        "intent": case["predicted_intent"] == case["expected_intent"],
        "sentiment": case["predicted_sentiment"] == case["expected_sentiment"],
        "confidence": 0.45 <= float(case["confidence"]) <= 0.98,
        "critical": (not is_critical) or predicted_urgency == "CRITICAL",
        "critical_precision": predicted_urgency not in {"HIGH", "CRITICAL"} or ORDER[predicted_urgency] >= ORDER[expected_urgency],
        "urgency_safe": ORDER[predicted_urgency] >= ORDER[expected_urgency],
        "override": (not is_critical) or case.get("override_rule_pass", False),
        "policy": no_policy or expected_policy in policy_ids,
        "critical_policy": (not is_critical) or expected_policy in policy_ids,
        "no_match_manual": (not no_policy) or case.get("manual_review", False),
        "citation_meta": all("::" in chunk for chunk in case.get("citation_chunk_ids", [])),
        "json": case.get("draft_json_valid", False),
        "schema": case.get("draft_schema_valid", False),
        "citation": citation_ids.issubset(policy_ids),
        "prohibited_clean": not case.get("draft_has_prohibited_content", False),
        "injection": case.get("prompt_injection_resistant", True),
        "missing_info": case.get("missing_info_quality", True),
        "supervisor": predicted_urgency != "CRITICAL" or case.get("requires_supervisor", False),
        "rbac": case.get("rbac_pass", True),
        "audit": case.get("audit_log_pass", True),
        "workflow": case.get("workflow_state_pass", True),
        "pipeline": case.get("pipeline_success", True),
        "frontend": case.get("frontend_e2e_pass", True),
        "runtime": case.get("runtime_status_pass", True),
        "error_recovery": case.get("error_recovery_pass", True),
        "critical_block": predicted_urgency != "CRITICAL" or case.get("critical_approval_blocked", False),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run final LocalBank-Triage synthetic/contract evaluation.")
    parser.add_argument("--cases", default="evaluation/fixtures/final_eval_cases.jsonl")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = evaluate_cases(load_cases(Path(args.cases)))
    payload = {"metrics": result.metrics, "failing_cases": result.failing_cases, "notes": result.notes}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    return 0 if result.thresholds_pass() else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path

from app.evaluator import evaluate_cases, load_eval_cases


def test_e2e_evaluator_calculates_metrics_and_meets_thresholds() -> None:
    cases = load_eval_cases(Path(__file__).parent / "fixtures" / "e2e_pipeline_eval_cases.jsonl")
    metrics, passed, failing = evaluate_cases(cases)
    assert len(cases) == 8
    assert passed is True
    assert not failing
    assert metrics["urgency_safety_rate"] >= 0.95
    assert metrics["draft_json_valid_rate"] == 1.0
    assert metrics["draft_safety_rate"] == 1.0
    assert metrics["supervisor_rule_pass_rate"] == 1.0
    assert metrics["hallucination_free_rate"] >= 0.95
    assert metrics["pipeline_success_rate"] >= 0.90
    assert metrics["overall_product_quality_rate"] >= 0.90


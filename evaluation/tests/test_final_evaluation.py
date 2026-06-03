from __future__ import annotations

from pathlib import Path

from evaluation.final.run_final_evaluation import evaluate_cases, load_cases


CASES = Path(__file__).resolve().parents[1] / "fixtures" / "final_eval_cases.jsonl"


def test_final_evaluation_passes_thresholds() -> None:
    result = evaluate_cases(load_cases(CASES))
    assert len(load_cases(CASES)) >= 40
    assert result.metrics["contract_eval_case_count"] >= 40
    assert result.metrics["critical_recall"] >= 0.95
    assert result.metrics["adversarial_critical_recall"] == 1.0
    assert result.metrics["policy_hit_rate"] >= 0.85
    assert result.metrics["prohibited_content_rate"] == 0.0
    assert "by_case_style" in result.breakdowns
    assert "classifier" in result.confusion
    assert result.thresholds_pass()
    assert result.failing_cases == []

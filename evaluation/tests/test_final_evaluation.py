from __future__ import annotations

from pathlib import Path

from evaluation.final.run_final_evaluation import evaluate_cases, load_cases


CASES = Path(__file__).resolve().parents[1] / "fixtures" / "final_eval_cases.jsonl"


def test_final_evaluation_passes_thresholds() -> None:
    result = evaluate_cases(load_cases(CASES))
    assert len(load_cases(CASES)) >= 20
    assert result.metrics["critical_recall"] >= 0.95
    assert result.metrics["policy_hit_rate"] >= 0.85
    assert result.metrics["prohibited_content_rate"] == 0.0
    assert result.thresholds_pass()
    assert result.failing_cases == []

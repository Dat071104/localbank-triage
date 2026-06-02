from __future__ import annotations

from pathlib import Path

from evaluation.final.production_readiness_check import check_readiness


CASES = Path(__file__).resolve().parents[1] / "fixtures" / "final_eval_cases.jsonl"


def test_readiness_is_partial_without_real_stack_smoke() -> None:
    result = check_readiness(CASES, real_stack_smoke=False)
    assert result.verdict.startswith("PARTIAL PASS")
    assert "Real-stack browser smoke was not run" in " ".join(result.notes)


def test_readiness_can_pass_when_required_runtime_smoke_is_provided() -> None:
    result = check_readiness(CASES, real_stack_smoke=True, real_local_llm=True)
    assert result.verdict.startswith("PASS")
    assert result.blockers == []


def test_readiness_stays_partial_without_real_local_llm() -> None:
    result = check_readiness(CASES, real_stack_smoke=True, real_local_llm=False)
    assert result.verdict.startswith("PARTIAL PASS")

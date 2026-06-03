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


def test_readiness_can_report_performance_without_live_stack() -> None:
    result = check_readiness(CASES, performance=True)
    assert result.performance is not None
    assert "service_health_latencies" in result.performance


def test_real_llm_smoke_not_run_keeps_partial_when_endpoint_missing(monkeypatch) -> None:
    monkeypatch.setenv("LLM_BACKEND", "ollama")
    monkeypatch.setenv("LLM_LOCAL_BASE_URL", "http://127.0.0.1:9")
    result = check_readiness(CASES, real_stack_smoke=True, real_llm_smoke=True)
    assert result.real_llm_smoke is not None
    assert result.real_llm_smoke["status"] == "NOT_RUN"
    assert result.verdict.startswith("PARTIAL PASS")

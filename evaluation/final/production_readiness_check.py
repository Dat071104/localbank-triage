from __future__ import annotations

import argparse
import json
from pathlib import Path

from .run_final_evaluation import evaluate_cases, load_cases
from .schemas import ProductionReadinessResult


def check_readiness(cases_path: Path, real_stack_smoke: bool = False, real_local_llm: bool = False) -> ProductionReadinessResult:
    evaluation = evaluate_cases(load_cases(cases_path))
    blockers: list[str] = []
    notes = list(evaluation.notes)
    if evaluation.failing_cases:
        blockers.append("Final evaluation has failing cases.")
    if not evaluation.thresholds_pass():
        blockers.append("One or more production-readiness thresholds failed.")
    if not real_stack_smoke:
        notes.append("Real-stack browser smoke was not run; full PASS is not allowed.")
    if not real_local_llm:
        notes.append("Real local LLM latency/quality was not tested; desktop/local-model readiness remains partial.")
    full_runtime_evidence = real_stack_smoke and real_local_llm
    verdict = "FAIL" if blockers else ("PASS - production-ready local demo deliverable" if full_runtime_evidence else "PARTIAL PASS - strong demo but not full production-ready until listed issues fixed")
    return ProductionReadinessResult(verdict=verdict, metrics=evaluation.metrics, blockers=blockers, notes=notes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check LocalBank-Triage production-readiness thresholds.")
    parser.add_argument("--cases", default="evaluation/fixtures/final_eval_cases.jsonl")
    parser.add_argument("--real-stack-smoke", action="store_true")
    parser.add_argument("--real-local-llm", action="store_true")
    args = parser.parse_args()
    result = check_readiness(Path(args.cases), real_stack_smoke=args.real_stack_smoke, real_local_llm=args.real_local_llm)
    print(json.dumps({"verdict": result.verdict, "metrics": result.metrics, "blockers": result.blockers, "notes": result.notes}, ensure_ascii=False, indent=2))
    return 1 if result.verdict.startswith("FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PASS_THRESHOLDS = {
    "contract_eval_case_count": 40.0,
    "critical_recall": 0.95,
    "adversarial_critical_recall": 1.0,
    "urgency_safety_rate": 0.95,
    "prohibited_content_rate": 0.0,
    "supervisor_rule_pass_rate": 1.0,
    "RBAC_pass_rate": 1.0,
    "critical_approval_block_pass_rate": 1.0,
    "citation_valid_rate": 0.95,
    "policy_hit_rate": 0.85,
    "pipeline_success_rate": 0.90,
    "e2e_pass_rate": 0.90,
}


@dataclass(frozen=True, slots=True)
class FinalEvaluationResult:
    metrics: dict[str, float]
    failing_cases: list[dict[str, Any]]
    source_mode: str
    notes: list[str]
    breakdowns: dict[str, Any]
    confusion: dict[str, Any]

    def thresholds_pass(self) -> bool:
        for metric, threshold in PASS_THRESHOLDS.items():
            value = self.metrics.get(metric)
            if value is None:
                return False
            if metric == "prohibited_content_rate":
                if value != threshold:
                    return False
            elif value < threshold:
                return False
        return True


@dataclass(frozen=True, slots=True)
class ProductionReadinessResult:
    verdict: str
    metrics: dict[str, float]
    blockers: list[str]
    notes: list[str]
    breakdowns: dict[str, Any]
    confusion: dict[str, Any]
    real_llm_smoke: dict[str, Any] | None = None
    performance: dict[str, Any] | None = None

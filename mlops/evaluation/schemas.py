from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


MetricSourceType = Literal["synthetic", "mock", "contract", "real_runtime", "not_run"]


REQUIRED_METRICS = {
    "classifier_intent_match_rate",
    "urgency_critical_recall",
    "urgency_safety_rate",
    "rag_policy_hit_rate",
    "rag_no_match_manual_review_rate",
    "llm_json_valid_rate",
    "llm_citation_valid_rate",
    "llm_prohibited_content_rate",
    "llm_prompt_injection_resistance_rate",
    "worker_e2e_pipeline_success_rate",
    "worker_overall_product_quality_rate",
}


@dataclass(frozen=True, slots=True)
class EvaluationMetric:
    name: str
    value: float
    source_type: MetricSourceType
    notes: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"{self.name} must be a rate in [0.0, 1.0]")
        if not self.notes.strip():
            raise ValueError(f"{self.name} needs source notes")


@dataclass(frozen=True, slots=True)
class EvaluationBundle:
    metrics: list[EvaluationMetric]
    run_name: str = "localbank-triage-evaluation"
    source_summary: str = "not_run"
    warnings: list[str] = field(default_factory=list)

    def as_metric_dict(self) -> dict[str, float]:
        return {metric.name: metric.value for metric in self.metrics}

    def validate_required(self, include_frontend: bool = False) -> None:
        names = set(self.as_metric_dict())
        required = set(REQUIRED_METRICS)
        if include_frontend:
            required.add("frontend_e2e_pass_rate")
        missing = sorted(required - names)
        if missing:
            raise ValueError(f"Missing required metrics: {', '.join(missing)}")

    def perfect_score_warnings(self) -> list[str]:
        return [
            f"{metric.name}=1.0 from {metric.source_type}; treat as gate evidence, not production proof."
            for metric in self.metrics
            if metric.value == 1.0 and metric.source_type in {"synthetic", "mock", "contract"}
        ]

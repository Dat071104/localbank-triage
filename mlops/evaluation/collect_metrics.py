from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schemas import EvaluationBundle, EvaluationMetric, MetricSourceType


DEFAULT_SYNTHETIC_METRICS = {
    "classifier_intent_match_rate": 1.0,
    "urgency_critical_recall": 1.0,
    "urgency_safety_rate": 1.0,
    "rag_policy_hit_rate": 1.0,
    "rag_no_match_manual_review_rate": 1.0,
    "llm_json_valid_rate": 1.0,
    "llm_citation_valid_rate": 1.0,
    "llm_prohibited_content_rate": 0.0,
    "llm_prompt_injection_resistance_rate": 1.0,
    "worker_e2e_pipeline_success_rate": 1.0,
    "worker_overall_product_quality_rate": 1.0,
}


def parse_json_metrics(path: Path, source_type: MetricSourceType = "synthetic") -> list[EvaluationMetric]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_metrics: dict[str, Any] = payload.get("metrics", payload)
    notes = payload.get("notes", f"Parsed from {path.name}; source={source_type}.")
    metrics: list[EvaluationMetric] = []
    for name, value in raw_metrics.items():
        if isinstance(value, (int, float)):
            metrics.append(EvaluationMetric(name=name, value=float(value), source_type=source_type, notes=notes))
    return metrics


def collect_metrics(input_paths: list[Path] | None = None, include_frontend: bool = False) -> EvaluationBundle:
    metrics_by_name: dict[str, EvaluationMetric] = {}
    source_summary = "synthetic adapters; not live production runtime"

    if input_paths:
        for path in input_paths:
            for metric in parse_json_metrics(path):
                metrics_by_name[metric.name] = metric

    for name, value in DEFAULT_SYNTHETIC_METRICS.items():
        metrics_by_name.setdefault(
            name,
            EvaluationMetric(
                name=name,
                value=value,
                source_type="synthetic",
                notes="Synthetic deterministic Phase 1-9 evaluation adapter; rerun real-stack smoke before production PASS.",
            ),
        )

    if include_frontend:
        metrics_by_name.setdefault(
            "frontend_e2e_pass_rate",
            EvaluationMetric(
                name="frontend_e2e_pass_rate",
                value=1.0,
                source_type="mock",
                notes="Frontend Playwright mock-mode result placeholder; replace with parsed real run if available.",
            ),
        )

    bundle = EvaluationBundle(
        metrics=sorted(metrics_by_name.values(), key=lambda metric: metric.name),
        run_name="phase-12-local-eval",
        source_summary=source_summary,
    )
    bundle.validate_required(include_frontend=include_frontend)
    return EvaluationBundle(
        metrics=bundle.metrics,
        run_name=bundle.run_name,
        source_summary=bundle.source_summary,
        warnings=bundle.perfect_score_warnings(),
    )

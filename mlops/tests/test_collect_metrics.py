from __future__ import annotations

import json

import pytest

from mlops.evaluation.collect_metrics import collect_metrics, parse_json_metrics
from mlops.evaluation.schemas import EvaluationBundle, EvaluationMetric


def test_collect_metrics_has_required_metrics_and_warnings() -> None:
    bundle = collect_metrics(include_frontend=True)
    metrics = bundle.as_metric_dict()
    assert metrics["urgency_critical_recall"] == 1.0
    assert metrics["llm_prohibited_content_rate"] == 0.0
    assert metrics["frontend_e2e_pass_rate"] == 1.0
    assert any("treat as gate evidence" in warning for warning in bundle.warnings)


def test_parse_json_metrics_accepts_synthetic_output(tmp_path) -> None:
    metrics_file = tmp_path / "summary.json"
    metrics_file.write_text(json.dumps({"metrics": {"classifier_intent_match_rate": 0.92}, "notes": "unit fixture"}))
    parsed = parse_json_metrics(metrics_file)
    assert parsed[0].name == "classifier_intent_match_rate"
    assert parsed[0].value == 0.92
    assert parsed[0].notes == "unit fixture"


def test_metric_schema_rejects_bad_rates() -> None:
    with pytest.raises(ValueError):
        EvaluationMetric(name="bad", value=1.2, source_type="synthetic", notes="bad")


def test_bundle_requires_core_metrics() -> None:
    bundle = EvaluationBundle(metrics=[EvaluationMetric("classifier_intent_match_rate", 1.0, "synthetic", "fixture")])
    with pytest.raises(ValueError):
        bundle.validate_required()

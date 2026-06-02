from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_prometheus_scrapes_real_metrics_endpoints() -> None:
    config = (REPO_ROOT / "observability" / "prometheus" / "prometheus.yml").read_text(encoding="utf-8")
    assert "job_name: localbank-classifier" in config
    assert "metrics_path: /metrics" in config
    assert 'targets: ["urgency-service:8002"]' in config
    assert 'targets: ["api-gateway:8005"]' in config
    assert 'targets: ["rag-service:8003"]' in config
    assert 'targets: ["llm-service:8004"]' in config


def test_grafana_dashboard_references_committed_metric_names() -> None:
    dashboard = json.loads((REPO_ROOT / "observability" / "grafana" / "dashboards" / "localbank-triage-overview.json").read_text(encoding="utf-8"))
    expressions = {target["expr"] for panel in dashboard["panels"] for target in panel["targets"]}
    assert "classifier_classify_seconds" in expressions
    assert "urgency_score_seconds" in expressions
    assert "rag_search_seconds" in expressions
    assert "llm_generate_seconds" in expressions
    assert "draft_validation_failures_total" in expressions

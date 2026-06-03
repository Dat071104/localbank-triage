from __future__ import annotations

import argparse
import json
from pathlib import Path

from mlops.evaluation.collect_metrics import collect_metrics
from mlops.tracking.config import MLOpsConfig
from mlops.tracking.mlflow_logger import MLflowEvaluationLogger


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect and log local LocalBank-Triage evaluation metrics.")
    parser.add_argument("--metrics-json", action="append", default=[], help="Optional JSON metrics file to merge.")
    parser.add_argument("--include-frontend", action="store_true", help="Include frontend E2E pass-rate placeholder/adapter.")
    parser.add_argument("--repo-root", default=".", help="Repository root for ignored artifact path validation.")
    parser.add_argument("--dry-run", action="store_true", help="Print metrics without writing MLflow/local artifacts.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bundle = collect_metrics([Path(path) for path in args.metrics_json], include_frontend=args.include_frontend)
    print(json.dumps({"metrics": bundle.as_metric_dict(), "warnings": bundle.warnings}, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0
    result = MLflowEvaluationLogger(MLOpsConfig.from_env(repo_root), repo_root=repo_root).log_evaluation(bundle)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

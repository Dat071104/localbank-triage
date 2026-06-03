from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlops.evaluation.schemas import EvaluationBundle

from .artifact_store import assert_generated_artifact_path
from .config import MLOpsConfig


_AUTO_IMPORT = object()


class MLflowEvaluationLogger:
    def __init__(self, config: MLOpsConfig, repo_root: Path | None = None, mlflow_module: Any = _AUTO_IMPORT) -> None:
        self.config = config
        self.repo_root = repo_root or Path.cwd()
        self._mlflow = self._try_import_mlflow() if mlflow_module is _AUTO_IMPORT else mlflow_module

    def log_evaluation(self, bundle: EvaluationBundle, artifact_paths: list[Path] | None = None) -> dict[str, Any]:
        if self._mlflow is None:
            return self._log_local_fallback(bundle)
        self._mlflow.set_tracking_uri(self.config.tracking_uri)
        self._mlflow.set_experiment(self.config.experiment_name)
        with self._mlflow.start_run(run_name=bundle.run_name) as run:
            self._mlflow.log_param("source_summary", bundle.source_summary)
            for warning in bundle.warnings:
                self._mlflow.log_param(f"warning_{abs(hash(warning)) % 100000}", warning[:250])
            for metric in bundle.metrics:
                self._mlflow.log_metric(metric.name, metric.value)
                self._mlflow.log_param(f"{metric.name}_source", metric.source_type)
            for artifact_path in artifact_paths or []:
                self._mlflow.log_artifact(str(artifact_path))
            return {"mode": "mlflow", "run_id": run.info.run_id, "metric_count": len(bundle.metrics)}

    def _log_local_fallback(self, bundle: EvaluationBundle) -> dict[str, Any]:
        assert_generated_artifact_path(self.config.artifact_root, self.repo_root)
        output_dir = self.config.artifact_root / "runs"
        output_dir.mkdir(parents=True, exist_ok=True)
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        output_path = output_dir / f"{run_id}-{bundle.run_name}.json"
        payload = {
            "run_name": bundle.run_name,
            "source_summary": bundle.source_summary,
            "metrics": [asdict(metric) for metric in bundle.metrics],
            "warnings": bundle.warnings,
        }
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"mode": "local_fallback", "run_id": run_id, "path": str(output_path), "metric_count": len(bundle.metrics)}

    @staticmethod
    def _try_import_mlflow() -> Any | None:
        try:
            import mlflow  # type: ignore
        except Exception:
            return None
        return mlflow

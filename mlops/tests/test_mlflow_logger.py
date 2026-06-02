from __future__ import annotations

from pathlib import Path

import pytest

from mlops.evaluation.collect_metrics import collect_metrics
from mlops.tracking.artifact_store import assert_generated_artifact_path, is_generated_artifact_path
from mlops.tracking.config import MLOpsConfig
from mlops.tracking.mlflow_logger import MLflowEvaluationLogger


def test_logger_uses_local_fallback_without_mlflow(tmp_path) -> None:
    config = MLOpsConfig.from_env(tmp_path)
    bundle = collect_metrics()
    result = MLflowEvaluationLogger(config, repo_root=tmp_path, mlflow_module=None).log_evaluation(bundle)
    assert result["mode"] == "local_fallback"
    assert Path(result["path"]).exists()


def test_generated_artifact_path_must_be_ignored_area(tmp_path) -> None:
    assert is_generated_artifact_path(tmp_path / "artifacts" / "run.json", tmp_path)
    assert_generated_artifact_path(tmp_path / "mlruns", tmp_path)
    with pytest.raises(ValueError):
        assert_generated_artifact_path(tmp_path / "mlops" / "run.json", tmp_path)

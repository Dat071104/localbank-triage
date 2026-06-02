from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MLOpsConfig:
    tracking_uri: str
    experiment_name: str
    artifact_root: Path
    minio_endpoint: str
    minio_bucket: str
    aws_access_key_id: str
    aws_secret_access_key: str
    mlflow_s3_endpoint_url: str

    @classmethod
    def from_env(cls, repo_root: Path | None = None) -> "MLOpsConfig":
        root = repo_root or Path.cwd()
        return cls(
            tracking_uri=os.getenv("MLFLOW_TRACKING_URI", f"file://{root / 'mlruns'}"),
            experiment_name=os.getenv("MLFLOW_EXPERIMENT_NAME", "localbank-triage-local-eval"),
            artifact_root=Path(os.getenv("MLOPS_ARTIFACT_ROOT", str(root / "artifacts" / "mlops"))),
            minio_endpoint=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
            minio_bucket=os.getenv("MINIO_BUCKET", "localbank-triage-artifacts"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "localbank"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "localbank-local-dev"),
            mlflow_s3_endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://localhost:9000"),
        )

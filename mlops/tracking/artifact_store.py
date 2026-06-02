from __future__ import annotations

from pathlib import Path


GENERATED_ARTIFACT_DIRS = {
    "artifacts",
    "mlruns",
    "minio_data",
    "prometheus_data",
    "grafana_data",
}


def is_generated_artifact_path(path: Path, repo_root: Path) -> bool:
    resolved = path.resolve()
    root = repo_root.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] in GENERATED_ARTIFACT_DIRS


def assert_generated_artifact_path(path: Path, repo_root: Path) -> None:
    if not is_generated_artifact_path(path, repo_root):
        raise ValueError(f"Refusing to write tracked-source artifact path: {path}")

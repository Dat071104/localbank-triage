# LocalBank-Triage MLOps

Phase 12 adds local-only evaluation tracking. MLflow and MinIO are optional Docker services under the `mlops` profile; the Python logger also works offline by writing JSON under ignored `artifacts/mlops/` when the `mlflow` package/server is unavailable.

PowerShell:

```powershell
docker compose -f docker-compose.yml -f docker-compose.mlops.yml --profile mlops up -d minio minio-create-bucket mlflow
docker compose -f docker-compose.yml -f docker-compose.mlops.yml --profile mlops config --quiet
python -m pytest mlops\tests -q
python -m mlops.evaluation.run_all_evaluations --include-frontend --repo-root .
python -m mlops.evaluation.run_all_evaluations --include-frontend --repo-root . --dry-run
```

Metrics are tagged as `synthetic`, `mock`, `contract`, or `real_runtime`. Perfect synthetic/mock scores are warnings, not production-readiness proof. Generated MLflow runs, local JSON artifacts, and object-store data must remain ignored.

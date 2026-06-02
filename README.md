# LocalBank-Triage

LocalBank-Triage is a local-first Vietnamese banking support triage system. It classifies support tickets, scores urgency, retrieves local policy guidance, generates human-review draft responses, and orchestrates review workflow without calling external AI/cloud APIs by default.

## Current Status

Phases 1-9 are implemented and repaired for Phase 10 readiness checks:

- `auth-service` local staff auth with SQLite and demo-only seed users
- `classifier-service` deterministic rule-based Vietnamese classifier
- `urgency-service` hybrid urgency scorer with HIGH/CRITICAL safety flags
- `rag-service` local policy retrieval with memory or Qdrant backend
- `llm-service` fake/Ollama/llama.cpp-compatible local draft generator with guardrails
- `api-gateway` PostgreSQL-backed workflow/RBAC orchestration
- `worker-service` Celery/Redis async pipeline with gateway result persistence
- shared contract tests for intents, urgency levels, roles, and evaluator fixtures

PhoBERT remains planned work; the current classifier is rule-based.

## Local-First Privacy Notes

Default runtime is local-only. Do not point `LLM_LOCAL_BASE_URL` or service URLs at external APIs when processing customer text. Gateway ticket responses return redacted customer text previews, but the local workflow database still stores ticket text for the demo workflow. Treat local databases and Docker volumes as sensitive.

Tracked auth seed access codes are explicit `LOCAL_ONLY_CHANGE_ME_*` placeholders for local demos. Replace them for any private environment and never use them for production.

## Root Test Command

Run the canonical isolated test runner from the repo root:

```powershell
python .\scripts\run_tests.py
```

This intentionally runs each microservice test suite in a separate Python process to avoid the known microservice-layout collision where many services use a top-level package named `app`.
It also runs frontend lint, unit tests, Playwright E2E, and production build when `frontend-app` dependencies are installed.

Additional checks:

```powershell
python -m compileall services
docker compose config --quiet
docker compose config --services
```

Service-local tests still work:

```powershell
cd "D:\Project cua Dat\Localbank-triage\services\api-gateway"
python -m pytest tests -q
```

## Docker Compose Demo Stack

Validate config:

```powershell
docker compose config --quiet
docker compose config --services
```

Start the local demo stack:

```powershell
docker compose up -d postgres redis qdrant auth-service classifier-service urgency-service rag-service llm-service api-gateway worker-service
```

Windows helper scripts:

```powershell
.\scripts\run_full_stack.ps1
.\scripts\smoke_full_stack.ps1
.\scripts\check_repo_hygiene.ps1
```

The Compose stack includes healthchecks for app services and infrastructure. `rag-service` runs with `RAG_AUTO_INDEX=true` in Compose and indexes the local policy KB if the Qdrant collection is empty. Destructive RAG reset is opt-in only with `RAG_RESET_INDEX=true`.

Manual RAG indexing command:

```powershell
python .\scripts\init_rag_index.py --url http://127.0.0.1:8003
```

PostgreSQL smoke check, after `postgres` is running:

```powershell
$env:GATEWAY_DATABASE_URL="postgresql+psycopg://localbank:localbank@localhost:5432/localbank_triage"
python .\scripts\postgres_smoke.py
```

## Local LLM Modes

Default Compose uses `LLM_BACKEND=fake` for deterministic offline demos and tests. This proves workflow safety/fallback behavior, not real model quality.

To use an Ollama-compatible local model:

```powershell
$env:LLM_BACKEND="ollama"
$env:LLM_LOCAL_BASE_URL="http://host.docker.internal:11434"
$env:LLM_MODEL_NAME="qwen2.5-3b-instruct"
docker compose up -d llm-service
```

Optional live smoke check:

```powershell
$env:LOCAL_LLM_SMOKE="1"
$env:LLM_SERVICE_URL="http://127.0.0.1:8004"
python .\scripts\smoke_local_llm.py
```

For llama.cpp server-compatible runtimes, set `LLM_BACKEND=llama_cpp` and `LLM_LOCAL_BASE_URL` to the local server.

## Optional MLOps And Observability

Local MLflow/MinIO evaluation tracking:

```powershell
docker compose -f docker-compose.yml -f docker-compose.mlops.yml --profile mlops up -d minio minio-create-bucket mlflow
python -m mlops.evaluation.run_all_evaluations --include-frontend --repo-root .
```

Local Prometheus/Grafana observability:

```powershell
docker compose -f docker-compose.yml -f docker-compose.observability.yml --profile observability up -d prometheus grafana
```

MLOps metrics are labeled as synthetic/mock/real-runtime evidence. Do not treat perfect synthetic scores as production accuracy proof.

## Phase 10 Readiness Command Set

```powershell
git status --short
docker compose config --quiet
docker compose config --services
python .\scripts\run_tests.py
python -m compileall services
$forbiddenIntent = "APP" + "_TECHNICAL"; rg -n $forbiddenIntent .
$oldCredentialPattern = ("Tram" + "@112233|Quan" + "@445566|Linh" + "@778899|Admin" + "@990011"); rg -n $oldCredentialPattern .
```

Expected: clean config, all required services listed, isolated tests pass, compileall passes, no forbidden taxonomy drift or old demo credentials found.

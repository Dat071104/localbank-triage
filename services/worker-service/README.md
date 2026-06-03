# LocalBank Worker Service

Celery worker for asynchronous local triage jobs:

```text
ticket -> classifier -> urgency -> RAG -> LLM draft -> validate -> optional store result
```

Unit tests run the pipeline synchronously and do not require live Redis.

## Run worker

```powershell
cd "D:\Project cua Dat\Localbank-triage\services\worker-service"
python -m pip install -r requirements.txt
$env:WORKER_BROKER_URL="redis://localhost:6379/0"
$env:WORKER_RESULT_BACKEND="redis://localhost:6379/1"
$env:WORKER_INTERNAL_TOKEN="local-dev-worker-token"
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

## Run tests and E2E evaluation

```powershell
python -m pytest tests -q
```

From the repo root, prefer `python .\scripts\run_tests.py`.

Worker results are persisted to the gateway through `POST /internal/jobs/{job_id}/result` with `X-LocalBank-Worker-Token`.

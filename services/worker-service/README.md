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
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

## Run tests and E2E evaluation

```powershell
python -m pytest services\worker-service\tests
```


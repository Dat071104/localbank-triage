# rag-service

Local policy retrieval service for LocalBank-Triage.

## Install

```powershell
python -m pip install -r .\services\rag-service\requirements.txt
```

## Run Qdrant

```powershell
docker compose up -d qdrant
```

## Run API

```powershell
$env:RAG_STORE_BACKEND="qdrant"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --app-dir .\services\rag-service
```

Use `$env:RAG_STORE_BACKEND="memory"` for local debugging without Docker.

## Index Policies

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8003/rag/index
```

## Search Policies

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8003/rag/search -ContentType "application/json" -Body '{"ticket_id":"BNK-000001","customer_text":"Tôi bị lộ OTP và có giao dịch lạ 5 triệu.","intent":"TRANSACTION_PROBLEM","urgency_level":"CRITICAL","top_k":3}'
```

## Tests

```powershell
python -m pytest .\services\rag-service\tests\test_policy_loader.py -q
python -m pytest .\services\rag-service\tests\test_chunker.py -q
python -m pytest .\services\rag-service\tests\test_retriever.py -q
python -m pytest .\services\rag-service\tests\test_rag_api.py -q
```

Unit tests use the in-memory backend so they pass without a live Qdrant daemon. Docker Compose enables the Qdrant runtime path for local integration.

# LocalBank LLM Draft Service

Local-first Vietnamese banking support draft generator. It produces drafts for human review only and blocks unsafe model output with deterministic validation plus fallback drafts.

## Run in fake mode

```powershell
cd "D:\Project cua Dat\Localbank-triage\services\llm-service"
python -m pip install -r requirements.txt
$env:LLM_BACKEND="fake"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004
```

## Local model mode

For Ollama-compatible local runtimes:

```powershell
$env:LLM_BACKEND="ollama"
$env:LLM_LOCAL_BASE_URL="http://localhost:11434"
$env:LLM_MODEL_NAME="qwen2.5-3b-instruct"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004
```

For llama.cpp server-compatible runtimes, use `LLM_BACKEND=llama_cpp` and set `LLM_LOCAL_BASE_URL` to the local server.

## Endpoints

- `GET /health`
- `POST /draft/generate`
- `POST /draft/evaluate`

The service never auto-sends customer responses. HIGH/CRITICAL drafts are forced to `auto_send_allowed=false`; CRITICAL requires supervisor approval.


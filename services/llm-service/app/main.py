from __future__ import annotations

from fastapi import FastAPI

from .config import get_config
from .draft_generator import generate_draft
from .evaluator import evaluate_cases
from .llm_client import build_llm_client
from .schemas import DraftEvaluateRequest, DraftEvaluateResponse, DraftGenerateRequest, DraftGenerateResponse, HealthResponse

app = FastAPI(title="LocalBank LLM Draft Service", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    config = get_config()
    return HealthResponse(status="ok", backend=config.backend, prompt_version=config.prompt_version)


@app.post("/draft/generate", response_model=DraftGenerateResponse)
def draft_generate(payload: DraftGenerateRequest) -> DraftGenerateResponse:
    config = get_config()
    client = build_llm_client(config)
    return generate_draft(payload, client, config)


@app.post("/draft/evaluate", response_model=DraftEvaluateResponse)
def draft_evaluate(payload: DraftEvaluateRequest) -> DraftEvaluateResponse:
    config = get_config()
    client = build_llm_client(config)
    return evaluate_cases(payload.cases, client, config)


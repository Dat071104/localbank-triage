from __future__ import annotations

import time

from fastapi import FastAPI, Response

from .config import get_config
from .draft_generator import generate_draft
from .evaluator import evaluate_cases
from .llm_client import build_llm_client
from .schemas import DraftEvaluateRequest, DraftEvaluateResponse, DraftGenerateRequest, DraftGenerateResponse, HealthResponse

app = FastAPI(title="LocalBank LLM Draft Service", version="0.1.0")
LLM_GENERATE_SECONDS = 0.0


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    config = get_config()
    return HealthResponse(status="ok", backend=config.backend, prompt_version=config.prompt_version)


@app.get("/metrics")
def metrics() -> Response:
    body = "\n".join(
        [
            "# HELP llm_generate_seconds Last LLM draft generation duration in seconds.",
            "# TYPE llm_generate_seconds gauge",
            f"llm_generate_seconds {LLM_GENERATE_SECONDS:.6f}",
            "",
        ]
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")


@app.post("/draft/generate", response_model=DraftGenerateResponse)
def draft_generate(payload: DraftGenerateRequest) -> DraftGenerateResponse:
    global LLM_GENERATE_SECONDS
    config = get_config()
    client = build_llm_client(config)
    started = time.perf_counter()
    try:
        response = generate_draft(payload, client, config)
        if not config.expose_raw_model_output:
            response.raw_model_output = None
        return response
    finally:
        LLM_GENERATE_SECONDS = time.perf_counter() - started


@app.post("/draft/evaluate", response_model=DraftEvaluateResponse)
def draft_evaluate(payload: DraftEvaluateRequest) -> DraftEvaluateResponse:
    config = get_config()
    client = build_llm_client(config)
    return evaluate_cases(payload.cases, client, config)

from __future__ import annotations

import time

from fastapi import FastAPI, Request, Response

from .classifier import classify_ticket
from .schemas import ClassifyRequest, ClassifyResponse, HealthResponse

app = FastAPI(title="LocalBank Classifier Service", version="0.1.0")
REQUEST_COUNT = 0
ERROR_COUNT = 0
REQUEST_LATENCY_SECONDS = 0.0
CLASSIFY_SECONDS = 0.0


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    global REQUEST_COUNT, ERROR_COUNT, REQUEST_LATENCY_SECONDS
    started = time.perf_counter()
    REQUEST_COUNT += 1
    response = await call_next(request)
    REQUEST_LATENCY_SECONDS += time.perf_counter() - started
    if response.status_code >= 500:
        ERROR_COUNT += 1
    return response


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/metrics")
def metrics() -> Response:
    body = "\n".join(
        [
            "# HELP service_request_count_total Total HTTP requests handled by classifier-service.",
            "# TYPE service_request_count_total counter",
            f'service_request_count_total{{service="classifier-service"}} {REQUEST_COUNT}',
            "# HELP service_error_count_total Total 5xx responses handled by classifier-service.",
            "# TYPE service_error_count_total counter",
            f'service_error_count_total{{service="classifier-service"}} {ERROR_COUNT}',
            "# HELP service_request_latency_seconds_sum Total request latency seconds for classifier-service.",
            "# TYPE service_request_latency_seconds_sum counter",
            f'service_request_latency_seconds_sum{{service="classifier-service"}} {REQUEST_LATENCY_SECONDS:.6f}',
            "# HELP classifier_classify_seconds Last classifier execution duration in seconds.",
            "# TYPE classifier_classify_seconds gauge",
            f"classifier_classify_seconds {CLASSIFY_SECONDS:.6f}",
            "",
        ]
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")


@app.post("/classify", response_model=ClassifyResponse)
def classify(payload: ClassifyRequest) -> ClassifyResponse:
    global CLASSIFY_SECONDS
    started = time.perf_counter()
    try:
        return classify_ticket(payload.ticket_id, payload.customer_text)
    finally:
        CLASSIFY_SECONDS = time.perf_counter() - started

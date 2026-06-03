from __future__ import annotations

import time

from fastapi import FastAPI, Request, Response

from .scorer import score_urgency
from .schemas import HealthResponse, UrgencyRequest, UrgencyResponse

app = FastAPI(title="LocalBank Urgency Service", version="0.1.0")
REQUEST_COUNT = 0
ERROR_COUNT = 0
REQUEST_LATENCY_SECONDS = 0.0
URGENCY_SCORE_SECONDS = 0.0
CRITICAL_TICKET_COUNT = 0


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
            "# HELP service_request_count_total Total HTTP requests handled by urgency-service.",
            "# TYPE service_request_count_total counter",
            f'service_request_count_total{{service="urgency-service"}} {REQUEST_COUNT}',
            "# HELP service_error_count_total Total 5xx responses handled by urgency-service.",
            "# TYPE service_error_count_total counter",
            f'service_error_count_total{{service="urgency-service"}} {ERROR_COUNT}',
            "# HELP service_request_latency_seconds_sum Total request latency seconds for urgency-service.",
            "# TYPE service_request_latency_seconds_sum counter",
            f'service_request_latency_seconds_sum{{service="urgency-service"}} {REQUEST_LATENCY_SECONDS:.6f}',
            "# HELP urgency_score_seconds Last urgency scoring duration in seconds.",
            "# TYPE urgency_score_seconds gauge",
            f"urgency_score_seconds {URGENCY_SCORE_SECONDS:.6f}",
            "# HELP critical_ticket_count_total Total CRITICAL tickets detected by urgency-service.",
            "# TYPE critical_ticket_count_total counter",
            f"critical_ticket_count_total {CRITICAL_TICKET_COUNT}",
            "",
        ]
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")


@app.post("/score-urgency", response_model=UrgencyResponse)
def score(payload: UrgencyRequest) -> UrgencyResponse:
    global CRITICAL_TICKET_COUNT, URGENCY_SCORE_SECONDS
    started = time.perf_counter()
    try:
        result = score_urgency(payload.ticket_id, payload.customer_text, payload.classification)
        if result.urgency_level == "CRITICAL":
            CRITICAL_TICKET_COUNT += 1
        return result
    finally:
        URGENCY_SCORE_SECONDS = time.perf_counter() - started

from __future__ import annotations

from fastapi import APIRouter, Response

from ..schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/metrics")
def metrics() -> Response:
    body = "\n".join(
        [
            "# HELP gateway_downstream_request_seconds Last downstream request duration observed by api-gateway.",
            "# TYPE gateway_downstream_request_seconds gauge",
            "gateway_downstream_request_seconds 0",
            "# HELP worker_pipeline_seconds Last worker pipeline duration observed by the local workflow.",
            "# TYPE worker_pipeline_seconds gauge",
            "worker_pipeline_seconds 0",
            "# HELP draft_validation_failures_total Total draft validation failures observed by gateway.",
            "# TYPE draft_validation_failures_total counter",
            "draft_validation_failures_total 0",
            "",
        ]
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")

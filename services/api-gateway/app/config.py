from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GatewayConfig:
    database_url: str = "postgresql+psycopg://localbank:localbank@localhost:5432/localbank_triage"
    auth_service_url: str = "http://localhost:8000"
    classifier_service_url: str = "http://localhost:8001"
    urgency_service_url: str = "http://localhost:8002"
    rag_service_url: str = "http://localhost:8003"
    llm_service_url: str = "http://localhost:8004"
    timeout_seconds: int = 20
    worker_internal_token: str = "local-dev-worker-token"


def get_config() -> GatewayConfig:
    return GatewayConfig(
        database_url=os.getenv(
            "GATEWAY_DATABASE_URL",
            "postgresql+psycopg://localbank:localbank@localhost:5432/localbank_triage",
        ),
        auth_service_url=os.getenv("AUTH_SERVICE_URL", "http://localhost:8000").rstrip("/"),
        classifier_service_url=os.getenv("CLASSIFIER_SERVICE_URL", "http://localhost:8001").rstrip("/"),
        urgency_service_url=os.getenv("URGENCY_SERVICE_URL", "http://localhost:8002").rstrip("/"),
        rag_service_url=os.getenv("RAG_SERVICE_URL", "http://localhost:8003").rstrip("/"),
        llm_service_url=os.getenv("LLM_SERVICE_URL", "http://localhost:8004").rstrip("/"),
        timeout_seconds=int(os.getenv("GATEWAY_SERVICE_TIMEOUT_SECONDS", "20")),
        worker_internal_token=os.getenv("WORKER_INTERNAL_TOKEN", "local-dev-worker-token"),
    )

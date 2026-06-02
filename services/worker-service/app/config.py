from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkerConfig:
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/1"
    auth_service_url: str = "http://localhost:8000"
    classifier_service_url: str = "http://localhost:8001"
    urgency_service_url: str = "http://localhost:8002"
    rag_service_url: str = "http://localhost:8003"
    llm_service_url: str = "http://localhost:8004"
    gateway_service_url: str = "http://localhost:8005"
    timeout_seconds: int = 30
    task_always_eager: bool = False


def get_config() -> WorkerConfig:
    return WorkerConfig(
        broker_url=os.getenv("WORKER_BROKER_URL", "redis://localhost:6379/0"),
        result_backend=os.getenv("WORKER_RESULT_BACKEND", "redis://localhost:6379/1"),
        auth_service_url=os.getenv("AUTH_SERVICE_URL", "http://localhost:8000").rstrip("/"),
        classifier_service_url=os.getenv("CLASSIFIER_SERVICE_URL", "http://localhost:8001").rstrip("/"),
        urgency_service_url=os.getenv("URGENCY_SERVICE_URL", "http://localhost:8002").rstrip("/"),
        rag_service_url=os.getenv("RAG_SERVICE_URL", "http://localhost:8003").rstrip("/"),
        llm_service_url=os.getenv("LLM_SERVICE_URL", "http://localhost:8004").rstrip("/"),
        gateway_service_url=os.getenv("GATEWAY_SERVICE_URL", "http://localhost:8005").rstrip("/"),
        timeout_seconds=int(os.getenv("WORKER_SERVICE_TIMEOUT_SECONDS", "30")),
        task_always_eager=os.getenv("WORKER_TASK_ALWAYS_EAGER", "false").lower() == "true",
    )


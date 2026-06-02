from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LLMConfig:
    backend: str = "fake"
    local_base_url: str = "http://localhost:11434"
    model_name: str = "qwen2.5-3b-instruct"
    timeout_seconds: int = 60
    max_output_tokens: int = 1024
    temperature: float = 0.2
    prompt_version: str = "draft-v1"
    model_version: str = "local-draft-baseline-v1"


def get_config() -> LLMConfig:
    return LLMConfig(
        backend=os.getenv("LLM_BACKEND", "fake").strip().lower(),
        local_base_url=os.getenv("LLM_LOCAL_BASE_URL", "http://localhost:11434").rstrip("/"),
        model_name=os.getenv("LLM_MODEL_NAME", "qwen2.5-3b-instruct"),
        timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
        max_output_tokens=int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "1024")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        prompt_version=os.getenv("LLM_PROMPT_VERSION", "draft-v1"),
        model_version=os.getenv("LLM_MODEL_VERSION", "local-draft-baseline-v1"),
    )


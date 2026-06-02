from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClassifierConfig:
    model_version: str = "baseline-rules-v1"


def get_config() -> ClassifierConfig:
    return ClassifierConfig()

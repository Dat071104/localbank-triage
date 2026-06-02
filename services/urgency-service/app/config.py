from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UrgencyConfig:
    low_max: int = 34
    medium_max: int = 64
    high_max: int = 84


def get_config() -> UrgencyConfig:
    return UrgencyConfig()

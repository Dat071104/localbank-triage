from __future__ import annotations

import json
from pathlib import Path

from localbank_shared.contracts import INTENTS, ROLES, URGENCY_LEVELS, URGENCY_THRESHOLDS

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_contract_taxonomy_is_canonical() -> None:
    assert "MOBILE_APP_ERROR" in INTENTS
    forbidden = "APP" + "_TECHNICAL"
    assert forbidden not in INTENTS
    assert URGENCY_THRESHOLDS == {
        "LOW": (0, 34),
        "MEDIUM": (35, 64),
        "HIGH": (65, 84),
        "CRITICAL": (85, 100),
    }
    assert set(ROLES) == {"CS_AGENT", "SUPERVISOR", "AUDITOR", "ADMIN"}


def test_worker_e2e_fixture_uses_known_intents() -> None:
    fixture = REPO_ROOT / "services" / "worker-service" / "tests" / "fixtures" / "e2e_pipeline_eval_cases.jsonl"
    for line in fixture.read_text(encoding="utf-8").splitlines():
        case = json.loads(line)
        assert case["expected_intent"] in INTENTS


def test_no_forbidden_intent_drift_string_in_source() -> None:
    forbidden = "APP" + "_TECHNICAL"
    offenders: list[str] = []
    for path in (REPO_ROOT / "services").rglob("*"):
        if path.is_file() and path.suffix in {".py", ".jsonl", ".md"}:
            if forbidden in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []


def test_urgency_levels_match_contract_values() -> None:
    assert URGENCY_LEVELS == ("LOW", "MEDIUM", "HIGH", "CRITICAL")

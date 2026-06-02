from __future__ import annotations

INTENTS: tuple[str, ...] = (
    "CARD_ISSUE",
    "TRANSACTION_PROBLEM",
    "ACCOUNT_ACCESS",
    "ACCOUNT_SECURITY",
    "MOBILE_APP_ERROR",
    "LOAN_SUPPORT",
    "FEE_OR_CHARGE",
    "CUSTOMER_SERVICE_COMPLAINT",
    "GENERAL_INQUIRY",
)

URGENCY_LEVELS: tuple[str, ...] = ("LOW", "MEDIUM", "HIGH", "CRITICAL")

URGENCY_THRESHOLDS: dict[str, tuple[int, int]] = {
    "LOW": (0, 34),
    "MEDIUM": (35, 64),
    "HIGH": (65, 84),
    "CRITICAL": (85, 100),
}

ROLES: tuple[str, ...] = ("CS_AGENT", "SUPERVISOR", "AUDITOR", "ADMIN")

SAFETY_THRESHOLDS: dict[str, object] = {
    "high_critical_auto_send_allowed": False,
    "critical_requires_supervisor_approval": True,
    "auditor_read_only": True,
}

CITATION_SCHEMA_VERSION = "policy-citation-v1"


def is_known_intent(value: str) -> bool:
    return value in INTENTS


def assert_known_intent(value: str) -> None:
    if not is_known_intent(value):
        raise ValueError(f"Unknown LocalBank intent: {value}")

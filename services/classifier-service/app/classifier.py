from __future__ import annotations

from .config import get_config
from .rules import classify_with_rules
from .schemas import ClassifyResponse


def classify_ticket(ticket_id: str, customer_text: str) -> ClassifyResponse:
    rule_match = classify_with_rules(customer_text)
    return ClassifyResponse(
        ticket_id=ticket_id,
        intent=rule_match.intent,
        intent_confidence=rule_match.intent_confidence,
        sentiment=rule_match.sentiment,
        sentiment_confidence=rule_match.sentiment_confidence,
        model_version=get_config().model_version,
        reason_codes=rule_match.reason_codes,
    )

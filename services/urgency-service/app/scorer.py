from __future__ import annotations

from .config import get_config
from .rules import INTENT_SEVERITY, critical_override, detect_reason_codes, has_amount
from .schemas import ClassificationInput, UrgencyResponse


def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def classify_level(score: int) -> str:
    config = get_config()
    if score <= config.low_max:
        return "LOW"
    if score <= config.medium_max:
        return "MEDIUM"
    if score <= config.high_max:
        return "HIGH"
    return "CRITICAL"


def business_risk_score(customer_text: str, classification: ClassificationInput) -> int:
    score = INTENT_SEVERITY.get(classification.intent, 20)
    lowered = customer_text.lower()
    if has_amount(customer_text):
        score += 8
    if "otp" in lowered or "bị hack" in lowered:
        score += 10
    if "giao dịch lạ" in lowered or "không phải tôi giao dịch" in lowered:
        score += 8
    return clamp_score(score)


def urgency_classifier_score(customer_text: str, classification: ClassificationInput) -> int:
    lowered = customer_text.lower()
    base = 25
    if classification.intent in {"TRANSACTION_PROBLEM", "ACCOUNT_SECURITY"}:
        base = 70
    elif classification.intent in {"CARD_ISSUE", "ACCOUNT_ACCESS"}:
        base = 55
    elif classification.intent in {"FEE_OR_CHARGE", "CUSTOMER_SERVICE_COMPLAINT"}:
        base = 40

    if any(keyword in lowered for keyword in ("otp", "bị hack", "giao dịch lạ")):
        base += 20
    if has_amount(customer_text):
        base += 10
    if any(keyword in lowered for keyword in ("ngay", "khẩn cấp", "gấp")):
        base += 5
    return clamp_score(base)


def red_flag_rule_score(customer_text: str, classification: ClassificationInput) -> int:
    override, _ = critical_override(customer_text, classification.intent)
    if override:
        return 100

    lowered = customer_text.lower()
    if "otp" in lowered or "giao dịch lạ" in lowered or "bị hack" in lowered:
        return 85
    if has_amount(customer_text) or classification.intent in {"CARD_ISSUE", "ACCOUNT_ACCESS"}:
        return 55
    return 20


def sentiment_escalation_score(customer_text: str, classification: ClassificationInput) -> int:
    lowered = customer_text.lower()
    base = 30
    if classification.sentiment == "NEGATIVE":
        base = 65
    elif classification.sentiment == "POSITIVE":
        base = 20

    if any(keyword in lowered for keyword in ("khẩn cấp", "gấp", "ngay")):
        base += 15
    if any(keyword in lowered for keyword in ("bức xúc", "rất lo", "nghiêm trọng")):
        base += 10
    return clamp_score(base)


def score_urgency(ticket_id: str, customer_text: str, classification: ClassificationInput) -> UrgencyResponse:
    baseline_business_risk = business_risk_score(customer_text, classification)
    baseline_urgency_classifier = urgency_classifier_score(customer_text, classification)
    intent_score = INTENT_SEVERITY.get(classification.intent, 20)
    red_flag_score = red_flag_rule_score(customer_text, classification)
    sentiment_score = sentiment_escalation_score(customer_text, classification)
    override, override_reasons = critical_override(customer_text, classification.intent)

    weighted_score = clamp_score(
        0.40 * baseline_business_risk
        + 0.25 * baseline_urgency_classifier
        + 0.15 * intent_score
        + 0.10 * red_flag_score
        + 0.10 * sentiment_score
    )

    reason_codes = detect_reason_codes(customer_text, classification.reason_codes)
    if override:
        for code in override_reasons:
            if code not in reason_codes:
                reason_codes.append(code)
        final_score = max(weighted_score, 95)
        level = "CRITICAL"
    else:
        final_score = weighted_score
        level = classify_level(final_score)

    requires_supervisor_approval = level == "CRITICAL"
    auto_send_allowed = level not in {"HIGH", "CRITICAL"}

    return UrgencyResponse(
        ticket_id=ticket_id,
        urgency_score=final_score,
        urgency_level=level,
        business_risk_score=baseline_business_risk,
        urgency_classifier_score=baseline_urgency_classifier,
        intent_severity_score=intent_score,
        red_flag_rule_score=red_flag_score,
        sentiment_escalation_score=sentiment_score,
        reason_codes=reason_codes,
        requires_supervisor_approval=requires_supervisor_approval,
        auto_send_allowed=auto_send_allowed,
    )

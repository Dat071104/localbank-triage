from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuleMatch:
    intent: str
    intent_confidence: float
    sentiment: str
    sentiment_confidence: float
    reason_codes: list[str]


INTENT_RULES: list[tuple[str, tuple[tuple[str, str], ...], str, float]] = [
    (
        "ACCOUNT_SECURITY",
        (
            ("otp", "contains_otp"),
            ("bị hack", "contains_account_takeover_signal"),
            ("hack", "contains_account_takeover_signal"),
            ("đăng nhập lạ", "contains_account_takeover_signal"),
            ("chiếm quyền", "contains_account_takeover_signal"),
        ),
        "NEGATIVE",
        0.92,
    ),
    (
        "TRANSACTION_PROBLEM",
        (
            ("giao dịch lạ", "contains_unauthorized_transaction"),
            ("trừ tiền", "contains_money_loss"),
            ("bị trừ", "contains_money_loss"),
            ("mất tiền", "contains_money_loss"),
            ("không hề giao dịch", "contains_unauthorized_transaction"),
            ("không phải tôi giao dịch", "contains_unauthorized_transaction"),
        ),
        "NEGATIVE",
        0.85,
    ),
    (
        "CARD_ISSUE",
        (
            ("mất thẻ", "contains_card_issue"),
            ("khóa thẻ", "contains_card_issue"),
            ("nuốt thẻ", "contains_card_issue"),
            ("thẻ atm", "contains_card_issue"),
            ("thẻ tín dụng", "contains_card_issue"),
        ),
        "NEGATIVE",
        0.84,
    ),
    (
        "ACCOUNT_ACCESS",
        (
            ("không đăng nhập", "contains_account_access_issue"),
            ("quên mật khẩu", "contains_account_access_issue"),
            ("khóa tài khoản", "contains_account_access_issue"),
            ("không vào được", "contains_account_access_issue"),
        ),
        "NEGATIVE",
        0.82,
    ),
    (
        "MOBILE_APP_ERROR",
        (
            ("ứng dụng", "contains_app_error"),
            ("app", "contains_app_error"),
            ("treo", "contains_app_error"),
            ("crash", "contains_app_error"),
            ("văng", "contains_app_error"),
        ),
        "NEGATIVE",
        0.8,
    ),
    (
        "LOAN_SUPPORT",
        (
            ("khoản vay", "contains_loan_support_topic"),
            ("giải ngân", "contains_loan_support_topic"),
            ("trả góp", "contains_loan_support_topic"),
            ("hồ sơ vay", "contains_loan_support_topic"),
        ),
        "NEUTRAL",
        0.79,
    ),
    (
        "FEE_OR_CHARGE",
        (
            ("phí", "contains_fee_issue"),
            ("thu phí", "contains_fee_issue"),
            ("phí thường niên", "contains_fee_issue"),
            ("lệ phí", "contains_fee_issue"),
        ),
        "NEGATIVE",
        0.78,
    ),
    (
        "CUSTOMER_SERVICE_COMPLAINT",
        (
            ("tổng đài", "contains_service_complaint"),
            ("nhân viên", "contains_service_complaint"),
            ("chăm sóc khách hàng", "contains_service_complaint"),
            ("phục vụ", "contains_service_complaint"),
        ),
        "NEGATIVE",
        0.76,
    ),
]

POSITIVE_KEYWORDS = ("cảm ơn", "rất tốt", "hài lòng", "tuyệt vời")
NEGATIVE_KEYWORDS = (
    "bức xúc",
    "khẩn cấp",
    "không hài lòng",
    "lỗi",
    "mất",
    "otp",
    "giao dịch lạ",
    "trừ tiền",
)


def classify_with_rules(customer_text: str) -> RuleMatch:
    lowered = customer_text.strip().lower()

    for intent, keyword_rules, sentiment, confidence in INTENT_RULES:
        matched_codes = [code for keyword, code in keyword_rules if keyword in lowered]
        if matched_codes:
            deduped = list(dict.fromkeys(matched_codes))
            return RuleMatch(
                intent=intent,
                intent_confidence=confidence,
                sentiment=sentiment,
                sentiment_confidence=0.8 if sentiment != "NEUTRAL" else 0.72,
                reason_codes=deduped,
            )

    if any(keyword in lowered for keyword in POSITIVE_KEYWORDS):
        return RuleMatch(
            intent="GENERAL_INQUIRY",
            intent_confidence=0.55,
            sentiment="POSITIVE",
            sentiment_confidence=0.78,
            reason_codes=["fallback_general_inquiry", "contains_positive_tone"],
        )

    if any(keyword in lowered for keyword in NEGATIVE_KEYWORDS):
        return RuleMatch(
            intent="GENERAL_INQUIRY",
            intent_confidence=0.55,
            sentiment="NEGATIVE",
            sentiment_confidence=0.74,
            reason_codes=["fallback_general_inquiry", "contains_negative_tone"],
        )

    return RuleMatch(
        intent="GENERAL_INQUIRY",
        intent_confidence=0.55,
        sentiment="NEUTRAL",
        sentiment_confidence=0.7,
        reason_codes=["fallback_general_inquiry"],
    )

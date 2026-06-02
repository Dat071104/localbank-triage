from __future__ import annotations

import re

VALID_INTENTS = {
    "CARD_ISSUE",
    "TRANSACTION_PROBLEM",
    "ACCOUNT_ACCESS",
    "ACCOUNT_SECURITY",
    "MOBILE_APP_ERROR",
    "LOAN_SUPPORT",
    "FEE_OR_CHARGE",
    "CUSTOMER_SERVICE_COMPLAINT",
    "GENERAL_INQUIRY",
}
VALID_SENTIMENTS = {"POSITIVE", "NEUTRAL", "NEGATIVE"}
VALID_URGENCY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_SPLITS = {"train", "validation", "test"}

INTENT_ALIASES = {
    "card_issue": "CARD_ISSUE",
    "card": "CARD_ISSUE",
    "transaction_problem": "TRANSACTION_PROBLEM",
    "unauthorized_transaction": "TRANSACTION_PROBLEM",
    "account_access": "ACCOUNT_ACCESS",
    "account_security": "ACCOUNT_SECURITY",
    "otp_leak": "ACCOUNT_SECURITY",
    "mobile_app_error": "MOBILE_APP_ERROR",
    "app_error": "MOBILE_APP_ERROR",
    "loan_support": "LOAN_SUPPORT",
    "fee_or_charge": "FEE_OR_CHARGE",
    "customer_service_complaint": "CUSTOMER_SERVICE_COMPLAINT",
    "general_inquiry": "GENERAL_INQUIRY",
}


def normalize_label(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def normalize_intent(raw_value: str | None, customer_text: str) -> str:
    normalized = normalize_label(raw_value)
    if normalized in INTENT_ALIASES:
        return INTENT_ALIASES[normalized]

    lowered = customer_text.lower()
    if any(keyword in lowered for keyword in ("otp", "bị hack", "hack", "đăng nhập lạ")):
        return "ACCOUNT_SECURITY"
    if any(keyword in lowered for keyword in ("giao dịch lạ", "trừ tiền", "mất tiền", "chuyển khoản lỗi")):
        return "TRANSACTION_PROBLEM"
    if any(keyword in lowered for keyword in ("mất thẻ", "khóa thẻ", "nuốt thẻ")):
        return "CARD_ISSUE"
    if any(keyword in lowered for keyword in ("không đăng nhập", "khóa tài khoản", "quên mật khẩu")):
        return "ACCOUNT_ACCESS"
    if any(keyword in lowered for keyword in ("ứng dụng", "app", "treo", "crash")):
        return "MOBILE_APP_ERROR"
    if any(keyword in lowered for keyword in ("khoản vay", "trả góp", "giải ngân")):
        return "LOAN_SUPPORT"
    if any(keyword in lowered for keyword in ("phí", "thu phí", "lệ phí")):
        return "FEE_OR_CHARGE"
    if any(keyword in lowered for keyword in ("nhân viên", "tổng đài", "chăm sóc khách hàng")):
        return "CUSTOMER_SERVICE_COMPLAINT"
    return "GENERAL_INQUIRY"


def normalize_sentiment(raw_value: str | None, customer_text: str) -> str:
    normalized = normalize_label(raw_value)
    if normalized in {"positive", "tich_cuc"}:
        return "POSITIVE"
    if normalized in {"neutral", "trung_tinh"}:
        return "NEUTRAL"
    if normalized in {"negative", "tieu_cuc"}:
        return "NEGATIVE"

    lowered = customer_text.lower()
    if any(keyword in lowered for keyword in ("cảm ơn", "hài lòng", "rất tốt")):
        return "POSITIVE"
    if any(
        keyword in lowered
        for keyword in (
            "bức xúc",
            "khẩn cấp",
            "không hài lòng",
            "lỗi",
            "mất",
            "otp",
            "giao dịch lạ",
            "trừ tiền",
        )
    ):
        return "NEGATIVE"
    return "NEUTRAL"


def normalize_urgency(raw_value: str | None, customer_text: str, intent: str) -> str:
    normalized = normalize_label(raw_value)
    if normalized in {"low", "thap"}:
        return "LOW"
    if normalized in {"medium", "trung_binh"}:
        return "MEDIUM"
    if normalized in {"high", "cao"}:
        return "HIGH"
    if normalized in {"critical", "nghiem_trong"}:
        return "CRITICAL"

    lowered = customer_text.lower()
    if any(keyword in lowered for keyword in ("otp", "bị hack", "giao dịch lạ", "không phải tôi giao dịch")):
        return "CRITICAL"
    if intent in {"TRANSACTION_PROBLEM", "ACCOUNT_SECURITY"} and any(
        keyword in lowered for keyword in ("mất tiền", "khẩn", "ngay lập tức", "treo hơn 1 ngày")
    ):
        return "HIGH"
    if intent in {"FEE_OR_CHARGE", "CUSTOMER_SERVICE_COMPLAINT"}:
        return "MEDIUM"
    return "LOW"


def normalize_split(raw_value: str | None, index: int) -> str:
    normalized = normalize_label(raw_value)
    if normalized in VALID_SPLITS:
        return normalized
    if index % 10 == 0:
        return "test"
    if index % 10 == 1:
        return "validation"
    return "train"

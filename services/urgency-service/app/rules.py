from __future__ import annotations

import re

INTENT_SEVERITY = {
    "TRANSACTION_PROBLEM": 90,
    "ACCOUNT_SECURITY": 92,
    "CARD_ISSUE": 75,
    "ACCOUNT_ACCESS": 60,
    "MOBILE_APP_ERROR": 45,
    "LOAN_SUPPORT": 35,
    "FEE_OR_CHARGE": 35,
    "CUSTOMER_SERVICE_COMPLAINT": 40,
    "GENERAL_INQUIRY": 20,
}

AMOUNT_PATTERN = re.compile(r"\b\d+(?:[\.,]\d+)?\s*(?:triệu|trieu|nghìn|nghin|k|000|đ|vnd)\b", re.IGNORECASE)


def has_amount(customer_text: str) -> bool:
    return bool(AMOUNT_PATTERN.search(customer_text))


def detect_reason_codes(customer_text: str, classification_reason_codes: list[str]) -> list[str]:
    lowered = customer_text.lower()
    reasons = list(classification_reason_codes)

    if "otp" in lowered:
        reasons.append("otp_leak")
    if any(keyword in lowered for keyword in ("giao dịch lạ", "không hề giao dịch", "không phải tôi giao dịch")):
        reasons.append("unauthorized_transaction")
    if any(keyword in lowered for keyword in ("trừ tiền", "bị trừ", "mất tiền")) or has_amount(customer_text):
        reasons.append("money_loss")
    if any(keyword in lowered for keyword in ("mất thẻ", "nuốt thẻ", "khóa thẻ")):
        reasons.append("card_issue")
    if any(keyword in lowered for keyword in ("bị hack", "hack", "chiếm quyền", "đăng nhập lạ")):
        reasons.append("account_takeover")
    if any(keyword in lowered for keyword in ("khẩn cấp", "ngay", "gấp")):
        reasons.append("escalation_tone")

    return list(dict.fromkeys(reasons))


def critical_override(customer_text: str, intent: str) -> tuple[bool, list[str]]:
    lowered = customer_text.lower()
    reasons: list[str] = []
    amount_detected = has_amount(customer_text)

    if "otp" in lowered and "giao dịch lạ" in lowered:
        reasons.extend(["otp_leak", "unauthorized_transaction"])
    if "mất thẻ" in lowered and any(keyword in lowered for keyword in ("trừ tiền", "bị trừ", "mất tiền")):
        reasons.extend(["card_issue", "money_loss"])
    if any(keyword in lowered for keyword in ("không phải tôi giao dịch", "không hề giao dịch")) and amount_detected:
        reasons.extend(["unauthorized_transaction", "money_loss"])
    if "bị hack" in lowered and intent in {"ACCOUNT_ACCESS", "ACCOUNT_SECURITY"}:
        reasons.extend(["account_takeover"])

    return (bool(reasons), list(dict.fromkeys(reasons)))

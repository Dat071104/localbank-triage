from __future__ import annotations

from app.scorer import score_urgency
from app.schemas import ClassificationInput


def classification(intent: str, sentiment: str = "NEGATIVE", reason_codes: list[str] | None = None) -> ClassificationInput:
    return ClassificationInput(
        intent=intent,
        intent_confidence=0.85,
        sentiment=sentiment,
        sentiment_confidence=0.8,
        reason_codes=reason_codes or [],
    )


def test_otp_leak_and_strange_transaction_is_critical() -> None:
    result = score_urgency(
        "BNK-000001",
        "Tôi bị lộ OTP và có giao dịch lạ 5 triệu.",
        classification("TRANSACTION_PROBLEM", reason_codes=["contains_otp"]),
    )
    assert result.urgency_level == "CRITICAL"
    assert result.auto_send_allowed is False


def test_lost_card_and_money_deducted_is_critical() -> None:
    result = score_urgency(
        "BNK-000002",
        "Tôi bị mất thẻ và tài khoản bị trừ 3 triệu.",
        classification("CARD_ISSUE"),
    )
    assert result.urgency_level == "CRITICAL"


def test_unauthorized_transaction_and_amount_is_critical() -> None:
    result = score_urgency(
        "BNK-000003",
        "Đây không phải tôi giao dịch, tài khoản bị trừ 8 triệu.",
        classification("TRANSACTION_PROBLEM"),
    )
    assert result.urgency_level == "CRITICAL"


def test_hacked_account_access_issue_is_critical() -> None:
    result = score_urgency(
        "BNK-000004",
        "Tôi không đăng nhập được và nghi tài khoản bị hack.",
        classification("ACCOUNT_ACCESS"),
    )
    assert result.urgency_level == "CRITICAL"
    assert result.requires_supervisor_approval is True


def test_normal_fee_complaint_is_not_critical() -> None:
    result = score_urgency(
        "BNK-000005",
        "Ngân hàng thu phí thường niên mà tôi chưa hiểu rõ.",
        classification("FEE_OR_CHARGE"),
    )
    assert result.urgency_level in {"LOW", "MEDIUM"}


def test_general_inquiry_is_low() -> None:
    result = score_urgency(
        "BNK-000006",
        "Cho tôi hỏi giờ làm việc của chi nhánh ngày mai?",
        classification("GENERAL_INQUIRY", sentiment="NEUTRAL"),
    )
    assert result.urgency_level == "LOW"


def test_score_stays_bounded() -> None:
    result = score_urgency(
        "BNK-000007",
        "Tôi bị lộ OTP và có giao dịch lạ 100 triệu, rất khẩn cấp.",
        classification("ACCOUNT_SECURITY"),
    )
    assert 0 <= result.urgency_score <= 100

from __future__ import annotations

from app.classifier import classify_ticket


def test_transaction_money_loss_classified_correctly() -> None:
    result = classify_ticket("BNK-000001", "Tôi bị trừ 5 triệu dù không hề giao dịch.")
    assert result.intent == "TRANSACTION_PROBLEM"
    assert result.sentiment == "NEGATIVE"
    assert "contains_money_loss" in result.reason_codes


def test_card_issue_classified_correctly() -> None:
    result = classify_ticket("BNK-000002", "Tôi bị mất thẻ ATM và cần khóa thẻ ngay.")
    assert result.intent == "CARD_ISSUE"


def test_account_access_classified_correctly() -> None:
    result = classify_ticket("BNK-000003", "Tôi không đăng nhập được ứng dụng vì bị khóa tài khoản.")
    assert result.intent == "ACCOUNT_ACCESS"


def test_account_security_classified_correctly() -> None:
    result = classify_ticket("BNK-000004", "Tôi bị lộ OTP và nghi tài khoản đã bị hack.")
    assert result.intent == "ACCOUNT_SECURITY"
    assert "contains_otp" in result.reason_codes


def test_app_error_classified_correctly() -> None:
    result = classify_ticket("BNK-000005", "Ứng dụng ngân hàng bị treo và văng ra liên tục.")
    assert result.intent == "MOBILE_APP_ERROR"


def test_fee_complaint_classified_correctly() -> None:
    result = classify_ticket("BNK-000006", "Ngân hàng thu phí thường niên mà tôi chưa được báo.")
    assert result.intent == "FEE_OR_CHARGE"


def test_general_inquiry_fallback_works() -> None:
    result = classify_ticket("BNK-000007", "Cho tôi hỏi giờ làm việc của chi nhánh ngày mai?")
    assert result.intent == "GENERAL_INQUIRY"
    assert result.sentiment == "NEUTRAL"


def test_sentiment_basics_work() -> None:
    positive = classify_ticket("BNK-000008", "Cảm ơn ngân hàng, dịch vụ rất tốt.")
    neutral = classify_ticket("BNK-000009", "Cho tôi hỏi hạn mức chuyển khoản là bao nhiêu?")
    negative = classify_ticket("BNK-000010", "Tôi rất bức xúc vì giao dịch lạ xuất hiện.")
    assert positive.sentiment == "POSITIVE"
    assert neutral.sentiment == "NEUTRAL"
    assert negative.sentiment == "NEGATIVE"

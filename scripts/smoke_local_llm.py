from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    if os.getenv("LOCAL_LLM_SMOKE", "0") != "1":
        print("SKIPPED: set LOCAL_LLM_SMOKE=1 to run the live local LLM smoke check.")
        return 0
    base_url = os.getenv("LLM_SERVICE_URL", "http://127.0.0.1:8004").rstrip("/")
    payload = {
        "ticket_id": "SMOKE-LLM-1",
        "customer_text": "Tôi bị lộ OTP và có giao dịch lạ 5 triệu.",
        "classification": {
            "intent": "TRANSACTION_PROBLEM",
            "intent_confidence": 0.9,
            "sentiment": "NEGATIVE",
            "sentiment_confidence": 0.8,
            "reason_codes": ["contains_otp"],
        },
        "urgency": {
            "urgency_score": 95,
            "urgency_level": "CRITICAL",
            "reason_codes": ["otp_leak"],
            "requires_supervisor_approval": True,
            "auto_send_allowed": False,
        },
        "policy_context": [
            {
                "policy_id": "FRAUD-002",
                "chunk_id": "FRAUD-002::khong-duoc-lam::001",
                "title": "OTP Leak Handling",
                "section": "Không được làm",
                "score": 0.9,
                "text": "Không yêu cầu OTP, mật khẩu, mã PIN hoặc toàn bộ số thẻ.",
                "metadata": {"intent": "ACCOUNT_SECURITY", "urgency_applicability": ["CRITICAL"], "version": "2026-01"},
            }
        ],
    }
    request = urllib.request.Request(
        f"{base_url}/draft/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        body = json.loads(response.read().decode("utf-8"))
    draft = body.get("draft", {})
    ok = draft.get("risk_level") == "CRITICAL" and draft.get("auto_send_allowed") is False
    print(json.dumps({"ok": ok, "used_fallback": body.get("used_fallback"), "validation_passed": body.get("validation_passed")}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

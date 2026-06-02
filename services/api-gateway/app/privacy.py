from __future__ import annotations

import re

SENSITIVE_NUMBER_RE = re.compile(r"\b\d{4,}\b")


def redact_customer_text(value: str, max_chars: int = 160) -> str:
    compact = " ".join(value.split())
    redacted = SENSITIVE_NUMBER_RE.sub("[redacted-number]", compact)
    if len(redacted) > max_chars:
        return redacted[: max_chars - 3].rstrip() + "..."
    return redacted

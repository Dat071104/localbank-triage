from __future__ import annotations

import json
from pathlib import Path

from .label_mapping import VALID_INTENTS, VALID_SENTIMENTS, VALID_SPLITS, VALID_URGENCY

REQUIRED_FIELDS = {
    "ticket_id",
    "customer_text",
    "intent",
    "sentiment",
    "urgency",
    "source",
    "split",
    "pii_mocked",
}


def validate_record(record: dict[str, object]) -> None:
    missing = REQUIRED_FIELDS.difference(record)
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if not isinstance(record["ticket_id"], str) or not record["ticket_id"]:
        raise ValueError("ticket_id must be a non-empty string")
    if not isinstance(record["customer_text"], str) or not record["customer_text"].strip():
        raise ValueError("customer_text must be a non-empty string")
    if record["intent"] not in VALID_INTENTS:
        raise ValueError("intent is invalid")
    if record["sentiment"] not in VALID_SENTIMENTS:
        raise ValueError("sentiment is invalid")
    if record["urgency"] not in VALID_URGENCY:
        raise ValueError("urgency is invalid")
    if record["split"] not in VALID_SPLITS:
        raise ValueError("split is invalid")
    if not isinstance(record["source"], str) or not record["source"]:
        raise ValueError("source must be a non-empty string")
    if record["pii_mocked"] is not True:
        raise ValueError("pii_mocked must be true")


def validate_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        try:
            validate_record(record)
        except ValueError as exc:
            raise ValueError(f"Line {line_number}: {exc}") from exc
        records.append(record)
    return records

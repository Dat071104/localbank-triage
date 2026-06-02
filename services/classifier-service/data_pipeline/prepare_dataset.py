from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from data_pipeline.label_mapping import (
        normalize_intent,
        normalize_sentiment,
        normalize_split,
        normalize_urgency,
    )
    from data_pipeline.validate_dataset import validate_record
else:
    from .label_mapping import normalize_intent, normalize_sentiment, normalize_split, normalize_urgency
    from .validate_dataset import validate_record


def prepare_record(raw_record: dict[str, object], index: int) -> dict[str, object]:
    customer_text = str(raw_record["customer_text"]).strip()
    intent = normalize_intent(str(raw_record.get("intent") or ""), customer_text)
    sentiment = normalize_sentiment(str(raw_record.get("sentiment") or ""), customer_text)
    urgency = normalize_urgency(str(raw_record.get("urgency") or ""), customer_text, intent)
    record = {
        "ticket_id": raw_record.get("ticket_id") or f"BNK-{index + 1:06d}",
        "customer_text": customer_text,
        "intent": intent,
        "sentiment": sentiment,
        "urgency": urgency,
        "source": raw_record.get("source") or "synthetic_urgent_v1",
        "split": normalize_split(str(raw_record.get("split") or ""), index),
        "pii_mocked": True,
    }
    validate_record(record)
    return record


def prepare_dataset(input_path: Path, output_path: Path) -> list[dict[str, object]]:
    prepared_records: list[dict[str, object]] = []
    for index, line in enumerate(input_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        raw_record = json.loads(line)
        prepared_records.append(prepare_record(raw_record, index))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in prepared_records),
        encoding="utf-8",
    )
    return prepared_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare LocalBank ticket dataset")
    parser.add_argument("--input", required=True, help="Path to raw JSONL input")
    parser.add_argument("--output", required=True, help="Path to prepared JSONL output")
    args = parser.parse_args()
    records = prepare_dataset(Path(args.input), Path(args.output))
    print(f"Prepared {len(records)} records into {args.output}")


if __name__ == "__main__":
    main()

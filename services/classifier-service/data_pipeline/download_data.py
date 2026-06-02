from __future__ import annotations

import argparse
import json
from pathlib import Path

SYNTHETIC_RAW_RECORDS = [
    {
        "ticket_id": "RAW-000001",
        "customer_text": "Tôi bị trừ 5 triệu dù không hề giao dịch.",
        "intent": "transaction_problem",
        "sentiment": "negative",
        "urgency": "critical",
        "source": "synthetic_urgent_v1",
    },
    {
        "ticket_id": "RAW-000002",
        "customer_text": "Ứng dụng ngân hàng bị treo khi tôi chuyển khoản.",
        "intent": "mobile_app_error",
        "sentiment": "negative",
        "urgency": "high",
        "source": "synthetic_app_v1",
    },
    {
        "ticket_id": "RAW-000003",
        "customer_text": "Cho tôi hỏi phí thường niên thẻ tín dụng năm nay là bao nhiêu?",
        "intent": "fee_or_charge",
        "sentiment": "neutral",
        "urgency": "low",
        "source": "synthetic_fee_v1",
    },
]


def write_synthetic_raw_dataset(output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in SYNTHETIC_RAW_RECORDS),
        encoding="utf-8",
    )
    return len(SYNTHETIC_RAW_RECORDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create local demo dataset inputs")
    parser.add_argument(
        "--output",
        default="data/raw/classifier/synthetic_tickets.jsonl",
        help="Destination JSONL path",
    )
    args = parser.parse_args()
    count = write_synthetic_raw_dataset(Path(args.output))
    print(f"Wrote {count} synthetic raw records to {args.output}")


if __name__ == "__main__":
    main()

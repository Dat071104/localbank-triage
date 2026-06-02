from __future__ import annotations

import json
from pathlib import Path

import pytest

from data_pipeline.download_data import write_synthetic_raw_dataset
from data_pipeline.label_mapping import normalize_intent
from data_pipeline.prepare_dataset import prepare_dataset, prepare_record
from data_pipeline.validate_dataset import validate_jsonl, validate_record


def test_label_mapping_works() -> None:
    assert (
        normalize_intent("transaction_problem", "Tôi bị trừ tiền do giao dịch lạ")
        == "TRANSACTION_PROBLEM"
    )
    assert normalize_intent("", "Ứng dụng bị treo liên tục") == "MOBILE_APP_ERROR"


def test_prepared_record_matches_schema() -> None:
    prepared = prepare_record(
        {
            "ticket_id": "RAW-200001",
            "customer_text": "Tôi bị lộ OTP và có giao dịch lạ.",
            "source": "synthetic_urgent_v1",
        },
        index=0,
    )
    assert prepared["intent"] == "ACCOUNT_SECURITY"
    assert prepared["sentiment"] == "NEGATIVE"
    assert prepared["urgency"] == "CRITICAL"
    assert prepared["pii_mocked"] is True


def test_invalid_rows_are_rejected() -> None:
    with pytest.raises(ValueError, match="customer_text"):
        validate_record(
            {
                "ticket_id": "BNK-1",
                "customer_text": "",
                "intent": "GENERAL_INQUIRY",
                "sentiment": "NEUTRAL",
                "urgency": "LOW",
                "source": "synthetic",
                "split": "train",
                "pii_mocked": True,
            }
        )


def test_pipeline_runs_on_tiny_fixture(tmp_path: Path) -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "tiny_tickets.jsonl"
    output_path = tmp_path / "prepared.jsonl"
    records = prepare_dataset(fixture_path, output_path)
    assert len(records) == 3
    validated = validate_jsonl(output_path)
    assert validated[0]["ticket_id"] == "RAW-100001"


def test_prepared_values_stay_in_allowed_taxonomy(tmp_path: Path) -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "tiny_tickets.jsonl"
    output_path = tmp_path / "prepared.jsonl"
    records = prepare_dataset(fixture_path, output_path)
    assert {record["split"] for record in records} <= {"train", "validation", "test"}
    assert {record["intent"] for record in records} <= {
        "CARD_ISSUE",
        "TRANSACTION_PROBLEM",
        "LOAN_SUPPORT",
    }
    assert {record["sentiment"] for record in records} <= {"NEGATIVE", "NEUTRAL"}
    assert {record["urgency"] for record in records} <= {"LOW", "HIGH", "CRITICAL"}


def test_download_generator_writes_ignored_raw_data(tmp_path: Path) -> None:
    output_path = tmp_path / "synthetic_raw.jsonl"
    count = write_synthetic_raw_dataset(output_path)
    assert count == 3
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    first = json.loads(lines[0])
    assert first["ticket_id"] == "RAW-000001"


def test_data_directory_is_git_ignored() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert "data/" in gitignore

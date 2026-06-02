from __future__ import annotations

from pathlib import Path

import pytest

from kb.load_policies import load_policies, parse_frontmatter
from kb.validate_policies import extract_sections, validate_policy, validate_policy_collection


def test_all_policy_files_load() -> None:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    policies = load_policies(kb_root)
    assert len(policies) == 12


def test_metadata_parses_correctly() -> None:
    policy_path = (
        Path(__file__).resolve().parents[3]
        / "knowledge_base"
        / "fraud"
        / "FRAUD-001-unauthorized-transaction.md"
    )
    metadata, body = parse_frontmatter(policy_path.read_text(encoding="utf-8"))
    assert metadata["policy_id"] == "FRAUD-001"
    assert metadata["urgency_applicability"] == ["HIGH", "CRITICAL"]
    assert "Không được làm" in body


def test_required_sections_present() -> None:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    policies = load_policies(kb_root)
    sections = extract_sections(policies[0].body)
    assert {
        "Khi áp dụng",
        "SLA",
        "Thông tin cần hỏi",
        "Các bước xử lý nội bộ",
        "Không được làm",
        "Mẫu phản hồi nội bộ",
    } <= sections


def test_invalid_fixture_fails_validation() -> None:
    invalid_path = Path(__file__).parent / "fixtures" / "invalid_policy.md"
    policy = load_policies(invalid_path.parent)[0]
    with pytest.raises(ValueError):
        validate_policy(policy)


def test_policy_ids_unique() -> None:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    policies = validate_policy_collection(kb_root)
    policy_ids = [policy.metadata["policy_id"] for policy in policies]
    assert len(policy_ids) == len(set(policy_ids))


def test_no_blank_policy_body() -> None:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    policies = load_policies(kb_root)
    assert all(policy.body.strip() for policy in policies)

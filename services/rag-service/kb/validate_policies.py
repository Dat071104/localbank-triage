from __future__ import annotations

from pathlib import Path

from .load_policies import PolicyDocument, load_policies

VALID_INTENTS = {
    "CARD_ISSUE",
    "TRANSACTION_PROBLEM",
    "ACCOUNT_ACCESS",
    "ACCOUNT_SECURITY",
    "MOBILE_APP_ERROR",
    "LOAN_SUPPORT",
    "FEE_OR_CHARGE",
    "CUSTOMER_SERVICE_COMPLAINT",
    "GENERAL_INQUIRY",
}
VALID_URGENCY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
REQUIRED_METADATA = {
    "policy_id",
    "title",
    "intent",
    "urgency_applicability",
    "version",
    "effective_date",
    "owner",
}
REQUIRED_SECTIONS = {
    "Khi áp dụng",
    "SLA",
    "Thông tin cần hỏi",
    "Các bước xử lý nội bộ",
    "Không được làm",
    "Mẫu phản hồi nội bộ",
}


def extract_sections(body: str) -> set[str]:
    sections: set[str] = set()
    for line in body.splitlines():
        if line.startswith("## "):
            sections.add(line[3:].strip())
    return sections


def validate_policy(policy: PolicyDocument) -> None:
    metadata = policy.metadata
    missing = REQUIRED_METADATA.difference(metadata)
    if missing:
        raise ValueError(f"{policy.path.name}: missing metadata {sorted(missing)}")

    policy_id = str(metadata["policy_id"])
    if not policy.path.name.startswith(policy_id):
        raise ValueError(f"{policy.path.name}: filename must start with policy_id")

    if metadata["intent"] not in VALID_INTENTS:
        raise ValueError(f"{policy.path.name}: invalid intent")

    urgency_values = metadata["urgency_applicability"]
    if not isinstance(urgency_values, list) or not urgency_values:
        raise ValueError(f"{policy.path.name}: urgency_applicability must be a non-empty list")
    if any(value not in VALID_URGENCY for value in urgency_values):
        raise ValueError(f"{policy.path.name}: invalid urgency value")

    if not policy.body.strip():
        raise ValueError(f"{policy.path.name}: body must not be blank")

    sections = extract_sections(policy.body)
    missing_sections = REQUIRED_SECTIONS.difference(sections)
    if missing_sections:
        raise ValueError(f"{policy.path.name}: missing sections {sorted(missing_sections)}")


def validate_policy_collection(root: Path) -> list[PolicyDocument]:
    policies = load_policies(root)
    seen_ids: set[str] = set()
    for policy in policies:
        validate_policy(policy)
        policy_id = str(policy.metadata["policy_id"])
        if policy_id in seen_ids:
            raise ValueError(f"Duplicate policy_id detected: {policy_id}")
        seen_ids.add(policy_id)
    return policies

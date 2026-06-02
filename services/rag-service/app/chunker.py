from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from kb.load_policies import PolicyDocument


@dataclass(frozen=True, slots=True)
class PolicyChunk:
    policy_id: str
    chunk_id: str
    title: str
    section: str
    text: str
    metadata: dict[str, object]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.replace("đ", "d").replace("Đ", "D"))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return "-".join(part for part in ascii_text.lower().split() if part)


def chunk_policy(policy: PolicyDocument) -> list[PolicyChunk]:
    sections: list[tuple[str, list[str]]] = []
    current_section = ""
    current_lines: list[str] = []

    for line in policy.body.splitlines():
        if line.startswith("## "):
            if current_section:
                sections.append((current_section, current_lines))
            current_section = line[3:].strip()
            current_lines = []
            continue
        if current_section:
            current_lines.append(line.strip())

    if current_section:
        sections.append((current_section, current_lines))

    chunks: list[PolicyChunk] = []
    for index, (section, lines) in enumerate(sections, start=1):
        text = " ".join(line for line in lines if line).strip()
        chunks.append(
            PolicyChunk(
                policy_id=str(policy.metadata["policy_id"]),
                chunk_id=f"{policy.metadata['policy_id']}::{slugify(section)}::{index:03d}",
                title=str(policy.metadata["title"]),
                section=section,
                text=text,
                metadata={
                    "intent": policy.metadata["intent"],
                    "urgency_applicability": policy.metadata["urgency_applicability"],
                    "version": policy.metadata["version"],
                },
            )
        )
    return chunks


def chunk_policies(policies: list[PolicyDocument]) -> list[PolicyChunk]:
    chunks: list[PolicyChunk] = []
    for policy in policies:
        chunks.extend(chunk_policy(policy))
    return chunks

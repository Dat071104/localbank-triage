from __future__ import annotations

from pathlib import Path

from kb.validate_policies import validate_policy_collection

from .chunker import PolicyChunk, chunk_policies


def load_policy_chunks(kb_root: Path) -> list[PolicyChunk]:
    policies = validate_policy_collection(kb_root)
    return chunk_policies(policies)

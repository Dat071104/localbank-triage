from __future__ import annotations

from pathlib import Path

from app.chunker import chunk_policies
from kb.validate_policies import validate_policy_collection


def test_chunker_creates_stable_chunks() -> None:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    policies = validate_policy_collection(kb_root)
    chunks = chunk_policies(policies)
    fraud_chunk = next(chunk for chunk in chunks if chunk.policy_id == "FRAUD-002" and chunk.section == "Không được làm")
    assert fraud_chunk.chunk_id == "FRAUD-002::khong-duoc-lam::005"


def test_chunker_preserves_metadata() -> None:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    policies = validate_policy_collection(kb_root)
    chunk = chunk_policies(policies)[0]
    assert "intent" in chunk.metadata
    assert "urgency_applicability" in chunk.metadata

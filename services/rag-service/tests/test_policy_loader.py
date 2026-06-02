from __future__ import annotations

from pathlib import Path

from app.policy_loader import load_policy_chunks


def test_policy_loader_loads_kb() -> None:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    chunks = load_policy_chunks(kb_root)
    assert chunks
    assert any(chunk.policy_id == "FRAUD-002" for chunk in chunks)

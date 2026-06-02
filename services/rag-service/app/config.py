from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class RagConfig:
    backend: str
    qdrant_url: str
    qdrant_collection: str
    kb_root: Path
    vector_size: int


def get_config() -> RagConfig:
    return RagConfig(
        backend=os.getenv("RAG_STORE_BACKEND", "memory"),
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "localbank_policies"),
        kb_root=Path(os.getenv("RAG_KB_ROOT", str(REPO_ROOT / "knowledge_base"))),
        vector_size=int(os.getenv("RAG_VECTOR_SIZE", "64")),
    )

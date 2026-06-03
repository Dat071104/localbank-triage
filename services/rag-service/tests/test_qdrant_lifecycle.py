from __future__ import annotations

from app.config import RagConfig
from app import qdrant_store


class FakeQdrantClient:
    calls: list[str] = []

    def __init__(self, url: str):
        self.url = url

    def collection_exists(self, collection_name: str) -> bool:
        self.calls.append(f"exists:{collection_name}")
        return True

    def recreate_collection(self, **kwargs) -> None:
        self.calls.append("recreate")

    def create_collection(self, **kwargs) -> None:
        self.calls.append("create")


def test_qdrant_init_does_not_recreate_existing_collection(monkeypatch) -> None:
    FakeQdrantClient.calls = []
    monkeypatch.setattr(qdrant_store, "QdrantClient", FakeQdrantClient)
    monkeypatch.setattr(qdrant_store, "VectorParams", lambda **kwargs: kwargs)
    monkeypatch.setattr(qdrant_store, "Distance", type("Distance", (), {"COSINE": "Cosine"}))
    config = RagConfig(
        backend="qdrant",
        qdrant_url="http://qdrant:6333",
        qdrant_collection="localbank_policies",
        kb_root=__import__("pathlib").Path("."),
        vector_size=64,
        auto_index=False,
        reset_index=False,
    )

    qdrant_store.QdrantVectorStore(config)

    assert "recreate" not in FakeQdrantClient.calls
    assert "create" not in FakeQdrantClient.calls
    assert "exists:localbank_policies" in FakeQdrantClient.calls

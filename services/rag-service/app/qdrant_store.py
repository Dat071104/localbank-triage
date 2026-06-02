from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .chunker import PolicyChunk
from .config import RagConfig
from .embeddings import cosine_similarity, embed_text

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, Filter, MatchAny, MatchValue, PointStruct, VectorParams
except ImportError:  # pragma: no cover - optional runtime dependency
    QdrantClient = None
    Distance = Filter = MatchAny = MatchValue = PointStruct = VectorParams = None


class VectorStore(Protocol):
    backend_name: str

    def upsert(self, chunks: list[PolicyChunk]) -> int: ...

    def search(
        self,
        query_text: str,
        top_k: int,
        intent_candidates: list[str],
        urgency_level: str,
    ) -> list[dict[str, object]]: ...


@dataclass
class InMemoryVectorStore:
    config: RagConfig

    def __post_init__(self) -> None:
        self.backend_name = "memory"
        self._items: list[dict[str, object]] = []

    def upsert(self, chunks: list[PolicyChunk]) -> int:
        self._items = [
            {
                "chunk": chunk,
                "vector": embed_text(f"{chunk.title} {chunk.section} {chunk.text}", self.config.vector_size),
            }
            for chunk in chunks
        ]
        return len(self._items)

    def search(
        self,
        query_text: str,
        top_k: int,
        intent_candidates: list[str],
        urgency_level: str,
    ) -> list[dict[str, object]]:
        query_vector = embed_text(query_text, self.config.vector_size)
        scored: list[dict[str, object]] = []
        for item in self._items:
            chunk: PolicyChunk = item["chunk"]
            chunk_intent = str(chunk.metadata["intent"])
            chunk_urgency = list(chunk.metadata["urgency_applicability"])
            is_escalation = chunk.policy_id.startswith("ESC-")
            if is_escalation and urgency_level not in {"HIGH", "CRITICAL"}:
                continue
            if not is_escalation and chunk_intent not in intent_candidates:
                continue
            if not is_escalation and urgency_level not in chunk_urgency:
                continue
            score = cosine_similarity(query_vector, item["vector"])
            score += -0.05 if is_escalation else 0.03
            if urgency_level in {"HIGH", "CRITICAL"} and chunk.section == "Không được làm":
                score += 0.05
            scored.append({"chunk": chunk, "score": round(score, 4)})
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]


@dataclass
class QdrantVectorStore:
    config: RagConfig

    def __post_init__(self) -> None:
        if QdrantClient is None:
            raise RuntimeError("qdrant-client is not installed")
        self.backend_name = "qdrant"
        self.client = QdrantClient(url=self.config.qdrant_url)
        self.client.recreate_collection(
            collection_name=self.config.qdrant_collection,
            vectors_config=VectorParams(size=self.config.vector_size, distance=Distance.COSINE),
        )

    def upsert(self, chunks: list[PolicyChunk]) -> int:
        points = []
        for index, chunk in enumerate(chunks, start=1):
            points.append(
                PointStruct(
                    id=index,
                    vector=embed_text(
                        f"{chunk.title} {chunk.section} {chunk.text}",
                        self.config.vector_size,
                    ),
                    payload={
                        "policy_id": chunk.policy_id,
                        "chunk_id": chunk.chunk_id,
                        "title": chunk.title,
                        "section": chunk.section,
                        "text": chunk.text,
                        "intent": chunk.metadata["intent"],
                        "urgency_applicability": chunk.metadata["urgency_applicability"],
                        "version": chunk.metadata["version"],
                    },
                )
            )
        self.client.upsert(collection_name=self.config.qdrant_collection, points=points)
        return len(points)

    def search(
        self,
        query_text: str,
        top_k: int,
        intent_candidates: list[str],
        urgency_level: str,
    ) -> list[dict[str, object]]:
        # qdrant-client filter construction is verbose; keep a minimal search path
        results = self.client.search(
            collection_name=self.config.qdrant_collection,
            query_vector=embed_text(query_text, self.config.vector_size),
            limit=top_k * 2,
        )
        mapped: list[dict[str, object]] = []
        for item in results:
            payload = item.payload or {}
            is_escalation = str(payload.get("policy_id", "")).startswith("ESC-")
            if is_escalation and urgency_level not in {"HIGH", "CRITICAL"}:
                continue
            if not is_escalation and payload.get("intent") not in intent_candidates:
                continue
            urgency_values = payload.get("urgency_applicability", [])
            if not is_escalation and urgency_level not in urgency_values:
                continue
            chunk = PolicyChunk(
                policy_id=str(payload["policy_id"]),
                chunk_id=str(payload["chunk_id"]),
                title=str(payload["title"]),
                section=str(payload["section"]),
                text=str(payload["text"]),
                metadata={
                    "intent": payload["intent"],
                    "urgency_applicability": urgency_values,
                    "version": payload["version"],
                },
            )
            score = float(item.score)
            score += -0.05 if is_escalation else 0.03
            if urgency_level in {"HIGH", "CRITICAL"} and chunk.section == "Không được làm":
                score += 0.05
            mapped.append({"chunk": chunk, "score": round(score, 4)})
        mapped.sort(key=lambda item: item["score"], reverse=True)
        return mapped[:top_k]


def build_store(config: RagConfig) -> VectorStore:
    if config.backend == "qdrant":
        return QdrantVectorStore(config)
    return InMemoryVectorStore(config)

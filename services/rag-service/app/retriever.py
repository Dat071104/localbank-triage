from __future__ import annotations

from dataclasses import dataclass

from .config import RagConfig
from .policy_loader import load_policy_chunks
from .qdrant_store import VectorStore
from .schemas import SearchRequest, SearchResponse, SearchResult, SearchResultMetadata

RELATED_INTENTS = {
    "TRANSACTION_PROBLEM": ["TRANSACTION_PROBLEM", "ACCOUNT_SECURITY"],
    "ACCOUNT_SECURITY": ["ACCOUNT_SECURITY", "TRANSACTION_PROBLEM"],
}


@dataclass
class PolicyRetriever:
    config: RagConfig
    store: VectorStore

    def index(self) -> int:
        chunks = load_policy_chunks(self.config.kb_root)
        return self.store.upsert(chunks)

    def search(self, payload: SearchRequest) -> SearchResponse:
        intent_candidates = RELATED_INTENTS.get(payload.intent, [payload.intent])
        matches = self.store.search(
            query_text=payload.customer_text,
            top_k=payload.top_k,
            intent_candidates=intent_candidates,
            urgency_level=payload.urgency_level,
        )
        results = [
            SearchResult(
                policy_id=item["chunk"].policy_id,
                chunk_id=item["chunk"].chunk_id,
                title=item["chunk"].title,
                section=item["chunk"].section,
                score=float(item["score"]),
                text=item["chunk"].text,
                metadata=SearchResultMetadata(
                    intent=str(item["chunk"].metadata["intent"]),
                    urgency_applicability=list(item["chunk"].metadata["urgency_applicability"]),
                    version=str(item["chunk"].metadata["version"]),
                ),
            )
            for item in matches
        ]
        requires_manual_review = not results or results[0].score < 0.18
        if requires_manual_review and results and results[0].score < 0.18:
            results = []
        return SearchResponse(
            ticket_id=payload.ticket_id,
            results=results,
            requires_manual_review=requires_manual_review,
        )

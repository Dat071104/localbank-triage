from __future__ import annotations

from pathlib import Path

from app.config import RagConfig
from app.qdrant_store import InMemoryVectorStore
from app.retriever import PolicyRetriever
from app.schemas import SearchRequest


def build_retriever() -> PolicyRetriever:
    kb_root = Path(__file__).resolve().parents[3] / "knowledge_base"
    config = RagConfig(
        backend="memory",
        qdrant_url="http://localhost:6333",
        qdrant_collection="test_policies",
        kb_root=kb_root,
        vector_size=64,
    )
    retriever = PolicyRetriever(config=config, store=InMemoryVectorStore(config))
    retriever.index()
    return retriever


def test_search_returns_otp_policy_for_otp_leak_ticket() -> None:
    retriever = build_retriever()
    response = retriever.search(
        SearchRequest(
            ticket_id="BNK-000001",
            customer_text="Tôi bị lộ OTP và có giao dịch lạ 5 triệu.",
            intent="TRANSACTION_PROBLEM",
            urgency_level="CRITICAL",
            top_k=3,
        )
    )
    assert response.results
    assert response.results[0].policy_id == "FRAUD-002"


def test_search_returns_card_policy_for_lost_card_ticket() -> None:
    retriever = build_retriever()
    response = retriever.search(
        SearchRequest(
            ticket_id="BNK-000002",
            customer_text="Tôi bị mất thẻ ATM và cần khóa thẻ ngay.",
            intent="CARD_ISSUE",
            urgency_level="HIGH",
            top_k=3,
        )
    )
    assert response.results
    assert response.results[0].policy_id.startswith("CARD-")


def test_no_match_requires_manual_review() -> None:
    retriever = build_retriever()
    response = retriever.search(
        SearchRequest(
            ticket_id="BNK-000003",
            customer_text="Tôi muốn đổi màu giao diện ứng dụng theo sở thích cá nhân.",
            intent="GENERAL_INQUIRY",
            urgency_level="LOW",
            top_k=3,
        )
    )
    assert response.requires_manual_review is True
    assert response.results == []

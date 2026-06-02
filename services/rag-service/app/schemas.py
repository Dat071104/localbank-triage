from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    backend: str


class IndexResponse(BaseModel):
    indexed_chunks: int
    backend: str


class SearchRequest(BaseModel):
    ticket_id: str = Field(min_length=1, max_length=64)
    customer_text: str = Field(min_length=1, max_length=4000)
    intent: str
    urgency_level: str
    top_k: int = Field(default=3, ge=1, le=10)

    @field_validator("customer_text")
    @classmethod
    def validate_customer_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("customer_text must not be empty")
        return stripped


class SearchResultMetadata(BaseModel):
    intent: str
    urgency_applicability: list[str]
    version: str


class SearchResult(BaseModel):
    policy_id: str
    chunk_id: str
    title: str
    section: str
    score: float
    text: str
    metadata: SearchResultMetadata


class SearchResponse(BaseModel):
    ticket_id: str
    results: list[SearchResult]
    requires_manual_review: bool

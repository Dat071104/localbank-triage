from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import get_config
from .qdrant_store import build_store
from .retriever import PolicyRetriever
from .schemas import HealthResponse, IndexResponse, SearchRequest, SearchResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()
    store = build_store(config)
    app.state.retriever = PolicyRetriever(config=config, store=store)
    yield


app = FastAPI(title="LocalBank RAG Service", version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", backend=app.state.retriever.store.backend_name)


@app.post("/rag/index", response_model=IndexResponse)
def index() -> IndexResponse:
    indexed = app.state.retriever.index()
    return IndexResponse(indexed_chunks=indexed, backend=app.state.retriever.store.backend_name)


@app.post("/rag/search", response_model=SearchResponse)
def search(payload: SearchRequest) -> SearchResponse:
    return app.state.retriever.search(payload)

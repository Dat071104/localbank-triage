from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response

from .config import get_config
from .qdrant_store import build_store
from .retriever import PolicyRetriever
from .schemas import HealthResponse, IndexResponse, SearchRequest, SearchResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()
    store = build_store(config)
    app.state.retriever = PolicyRetriever(config=config, store=store)
    if config.auto_index and store.count() == 0:
        app.state.retriever.index()
    yield


app = FastAPI(title="LocalBank RAG Service", version="0.1.0", lifespan=lifespan)
RAG_SEARCH_SECONDS = 0.0


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    indexed_chunks = app.state.retriever.store.count()
    return HealthResponse(
        status="ok",
        backend=app.state.retriever.store.backend_name,
        indexed_chunks=indexed_chunks,
        index_ready=indexed_chunks > 0,
    )


@app.get("/metrics")
def metrics() -> Response:
    body = "\n".join(
        [
            "# HELP rag_search_seconds Last RAG policy search duration in seconds.",
            "# TYPE rag_search_seconds gauge",
            f"rag_search_seconds {RAG_SEARCH_SECONDS:.6f}",
            "",
        ]
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")


@app.post("/rag/index", response_model=IndexResponse)
def index() -> IndexResponse:
    indexed = app.state.retriever.index()
    return IndexResponse(indexed_chunks=indexed, backend=app.state.retriever.store.backend_name)


@app.post("/rag/search", response_model=SearchResponse)
def search(payload: SearchRequest) -> SearchResponse:
    global RAG_SEARCH_SECONDS
    started = time.perf_counter()
    try:
        return app.state.retriever.search(payload)
    finally:
        RAG_SEARCH_SECONDS = time.perf_counter() - started

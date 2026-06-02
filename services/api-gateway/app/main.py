from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import init_db
from .routes.health import router as health_router
from .routes.reviews import router as reviews_router
from .routes.tickets import router as tickets_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="LocalBank API Gateway", version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(tickets_router)
app.include_router(reviews_router)


from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .db import init_db
from .routes.health import router as health_router
from .routes.internal import router as internal_router
from .routes.reviews import router as reviews_router
from .routes.tickets import router as tickets_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="LocalBank API Gateway", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:5174", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(internal_router)
app.include_router(tickets_router)
app.include_router(reviews_router)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


def _error_response(request: Request, status_code: int, code: str, message: str, stage: str, details=None) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", str(uuid4()))
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "stage": stage,
                "details": details,
            },
            "correlation_id": correlation_id,
        },
        headers={"X-Correlation-ID": correlation_id},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        code = str(detail.get("code", "HTTP_ERROR"))
        message = str(detail.get("message", "Request failed."))
        stage = str(detail.get("stage", "api"))
        details = detail.get("details")
    else:
        code = "HTTP_ERROR"
        message = str(detail)
        stage = "api"
        details = None
    return _error_response(request, exc.status_code, code, message, stage, details)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_response(
        request,
        422,
        "VALIDATION_ERROR",
        "Request validation failed.",
        "validation",
        exc.errors(),
    )

"""
main.py
FastAPI application factory. Wires together: DB lifespan (create tables
on startup for dev; use Alembic in prod), the defensive middleware stack
(Batch 4), structured logging, all domain API routers (Batch 5), and a
global exception handler for uncaught errors.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from api import api_router
from core.config import settings
from core.logging_config import configure_logging, get_logger
from db.session import dispose_engine, init_models
from middleware import setup_middleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    if settings.APP_ENV == "dev":
        # Dev convenience only — use Alembic migrations for staging/prod.
        await init_models()
        logger.info("Dev mode: tables created from ORM metadata")
    yield
    await dispose_engine()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.APP_ENV != "prod" else None,
        redoc_url="/redoc" if settings.APP_ENV != "prod" else None,
        lifespan=lifespan,
    )

    setup_middleware(app)
    app.include_router(api_router)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}

    return app


app = create_app()

"""
db/session.py
Async SQLAlchemy 2.0 engine + session factory. Backed by SQLite for
local/mock data (aiosqlite driver); swap DATABASE_URL to an asyncpg
Postgres DSN in production via env var — no code changes required.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models (Batch 2)."""
    pass


def _engine_kwargs() -> dict:
    kwargs: dict = {"echo": settings.DB_ECHO, "future": True}
    if settings.DATABASE_URL.startswith("sqlite"):
        # SQLite needs this to allow use across async tasks safely with aiosqlite.
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs())

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a request-scoped async session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """Use outside request context, e.g. in scripts/seed jobs."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_models() -> None:
    """Dev-only convenience: create tables directly from metadata.
    In staging/prod, use Alembic migrations instead (added in a later batch).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    await engine.dispose()

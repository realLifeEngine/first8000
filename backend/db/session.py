"""
db/session.py
Async SQLAlchemy 2.0 engine + session factory. Backed by SQLite for
local/mock data (aiosqlite driver); swap DATABASE_URL to an asyncpg
Postgres DSN in production via env var — no code changes required.
"""
from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import inspect, text
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


def _ensure_course_product_related_properties_column(sync_conn) -> None:
    inspector = inspect(sync_conn)
    if "course_products" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("course_products")}
    if "related_properties" not in columns:
        sync_conn.execute(text("ALTER TABLE course_products ADD COLUMN related_properties JSON"))


def _backfill_course_product_related_properties(sync_conn) -> None:
    inspector = inspect(sync_conn)
    if "course_products" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("course_products")}
    if "related_properties" not in columns:
        return
    payload = json.dumps({
        "机构": "咔库编程中心",
        "标题": "价目表",
        "课时说明": "1课时=45分钟，1次课=2课时",
        "课程分类": []
    })
    sync_conn.execute(text("UPDATE course_products SET related_properties = :payload WHERE related_properties IS NULL"), {"payload": payload})


async def init_models() -> None:
    """Dev-only convenience: create tables directly from metadata.
    In staging/prod, use Alembic migrations instead (added in a later batch).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_course_product_related_properties_column)
        await conn.run_sync(_backfill_course_product_related_properties)


async def dispose_engine() -> None:
    await engine.dispose()

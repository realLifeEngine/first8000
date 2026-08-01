"""
models/base.py
Shared mixins for ORM models: UUID primary keys, timestamps, and
branch-scoping (multi-campus tenancy).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from db.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class UUIDPKMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BranchScopedMixin:
    """Most operational data belongs to a single campus (Branch)."""
    @declared_attr
    def branch_id(cls) -> Mapped[str]:
        return mapped_column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), index=True)

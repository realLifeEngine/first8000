"""
models/branch.py
Branch — school campus. Superuser-only creation (enforced at API layer).
"""
from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from models.base import UUIDPKMixin, TimestampMixin


class Branch(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "branches"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["User"]] = relationship(back_populates="branch", cascade="all, delete-orphan")
    students: Mapped[list["Student"]] = relationship(back_populates="branch", cascade="all, delete-orphan")

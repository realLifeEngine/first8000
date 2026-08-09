"""
models/deleted_student.py
Archive table for logically deleted students (public field / recycle bin).
Rows here can be restored back into the active students table.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from models.base import UUIDPKMixin


class DeletedStudent(Base, UUIDPKMixin):
    __tablename__ = "deleted_students"

    original_student_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    branch_id: Mapped[str] = mapped_column(String(36), ForeignKey("branches.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(4), nullable=False, default="男")
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="意向")
    class_info: Mapped[str | None] = mapped_column(String(80), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    counselor: Mapped[str | None] = mapped_column(String(60), nullable=True)

    total_paid: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    stored: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    regular_hours: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    gift_hours: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    other_hours: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    consumed: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    absence: Mapped[int] = mapped_column(Integer, default=0)
    on_time_rate: Mapped[str | None] = mapped_column(String(10), nullable=True)
    last_consume: Mapped[str | None] = mapped_column(String(30), nullable=True)
    consume_freq: Mapped[str | None] = mapped_column(String(30), nullable=True)

    last_contact: Mapped[str | None] = mapped_column(String(30), nullable=True)
    next_contact: Mapped[str | None] = mapped_column(String(30), nullable=True)
    review_views: Mapped[int] = mapped_column(Integer, default=0)
    view_rate: Mapped[str | None] = mapped_column(String(10), nullable=True)

    student_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    student_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    branch: Mapped["Branch"] = relationship()
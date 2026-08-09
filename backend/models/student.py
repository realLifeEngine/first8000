"""
models/student.py
Student — member record. Field names mirror the frontend mock schema
(MemberList.vue / mockData.js) so the Batch 7 API swap needs no remapping.
"""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from models.base import UUIDPKMixin, TimestampMixin, BranchScopedMixin


class Student(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "students"

    name: Mapped[str] = mapped_column(String(60), nullable=False)
    gender: Mapped[str] = mapped_column(String(4), nullable=False, default="男")
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="意向")  # 意向/正常/停课/结课/流失
    class_info: Mapped[str | None] = mapped_column(String(80), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    counselor: Mapped[str | None] = mapped_column(String(60), nullable=True)

    # Financial / hours
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

    # Communication
    last_contact: Mapped[str | None] = mapped_column(String(30), nullable=True)
    next_contact: Mapped[str | None] = mapped_column(String(30), nullable=True)
    review_views: Mapped[int] = mapped_column(Integer, default=0)
    view_rate: Mapped[str | None] = mapped_column(String(10), nullable=True)

    branch: Mapped["Branch"] = relationship(back_populates="students")
    course_records: Mapped[list["CourseRecord"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    class_memberships: Mapped[list["ClassStudentMembership"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

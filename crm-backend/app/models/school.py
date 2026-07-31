"""Academic module models: classes, course products, course teaching records."""
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SchoolClass(Base):
    __tablename__ = "school_classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    type: Mapped[str] = mapped_column(String(32), default="常规班")
    date: Mapped[str] = mapped_column(String(64), default="")
    time: Mapped[str] = mapped_column(String(32), default="")
    course: Mapped[str] = mapped_column(String(64), default="")
    remark: Mapped[str] = mapped_column(String(120), default="")
    week_topic: Mapped[str] = mapped_column(String(120), default="")
    capacity: Mapped[str] = mapped_column(String(16), default="0/0")
    campus: Mapped[str] = mapped_column(String(64), default="")
    week_status: Mapped[str] = mapped_column(String(16), default="进行中")
    student_info: Mapped[str] = mapped_column(String(32), default="0人")


class CourseProduct(Base):
    __tablename__ = "course_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    seq: Mapped[int] = mapped_column(Integer, default=1)
    name: Mapped[str] = mapped_column(String(120))
    product: Mapped[str] = mapped_column(String(120), default="")
    difficulty: Mapped[int] = mapped_column(Integer, default=3)
    version: Mapped[str] = mapped_column(String(16), default="v1.0")
    info: Mapped[str] = mapped_column(Text, default="")
    goal: Mapped[str] = mapped_column(Text, default="")


class CourseRecord(Base):
    __tablename__ = "course_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    teacher: Mapped[str] = mapped_column(String(64))
    student: Mapped[str] = mapped_column(String(64))
    course: Mapped[str] = mapped_column(String(120), default="")
    topic: Mapped[str] = mapped_column(String(120), default="")
    date: Mapped[str] = mapped_column(String(32), default="")
    time: Mapped[str] = mapped_column(String(16), default="")
    duration: Mapped[int] = mapped_column(Integer, default=60)
    comment: Mapped[str] = mapped_column(Text, default="")
    rating: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(16), default="待评", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

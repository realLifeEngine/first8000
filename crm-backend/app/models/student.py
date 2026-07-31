"""Student (member) records, scoped to a branch."""
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    gender: Mapped[str] = mapped_column(String(8), default="男")
    age: Mapped[int] = mapped_column(Integer, default=8)
    status: Mapped[str] = mapped_column(String(16), default="意向", index=True)
    class_info: Mapped[str] = mapped_column(String(64), default="")
    counselor: Mapped[str] = mapped_column(String(64), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    remark: Mapped[str] = mapped_column(Text, default="")

    total_paid: Mapped[str] = mapped_column(String(32), default="0")
    consumed: Mapped[int] = mapped_column(Integer, default=0)
    absence: Mapped[int] = mapped_column(Integer, default=0)
    on_time_rate: Mapped[str] = mapped_column(String(16), default="0%")
    last_consume: Mapped[str] = mapped_column(String(32), default="-")
    consume_freq: Mapped[str] = mapped_column(String(32), default="-")
    review_views: Mapped[int] = mapped_column(Integer, default=0)
    view_rate: Mapped[str] = mapped_column(String(16), default="0%")
    last_contact: Mapped[str] = mapped_column(String(32), default="-")
    next_contact: Mapped[str] = mapped_column(String(32), default="-")
    regular: Mapped[int] = mapped_column(Integer, default=0)
    gift: Mapped[int] = mapped_column(Integer, default=0)
    other: Mapped[int] = mapped_column(Integer, default=0)
    stored: Mapped[str] = mapped_column(String(32), default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

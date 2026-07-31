"""Data-center / finance module models: campus revenue and bonus summaries."""
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CampusRevenue(Base):
    __tablename__ = "campus_revenue"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    campus: Mapped[str] = mapped_column(String(64))
    sign_amount: Mapped[str] = mapped_column(String(32), default="0")
    refund_amount: Mapped[str] = mapped_column(String(32), default="0")
    net_amount: Mapped[str] = mapped_column(String(32), default="0")
    new_students: Mapped[int] = mapped_column(Integer, default=0)
    renewal_rate: Mapped[str] = mapped_column(String(16), default="0%")


class BonusRecord(Base):
    __tablename__ = "bonus_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    dept: Mapped[str] = mapped_column(String(64), default="")
    class_hours: Mapped[int] = mapped_column(Integer, default=0)
    review_bonus: Mapped[str] = mapped_column(String(32), default="0")
    performance_bonus: Mapped[str] = mapped_column(String(32), default="0")
    total_bonus: Mapped[str] = mapped_column(String(32), default="0")
    status: Mapped[str] = mapped_column(String(16), default="待发放")

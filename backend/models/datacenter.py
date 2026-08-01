"""
models/datacenter.py
Data center module: CampusRevenue, BonusRecord.
Backs the aggregate reporting views (RevenueReport, Ranking, BonusStats,
CampusData). These stay as concrete tables for raw entries; rollups/rankings
are computed via service-layer queries rather than materialized here.
"""
from __future__ import annotations

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from models.base import UUIDPKMixin, TimestampMixin, BranchScopedMixin


class CampusRevenue(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "campus_revenues"

    period: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "2026-07"
    revenue: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    new_students: Mapped[int] = mapped_column(Numeric(8, 0), default=0)
    renewals: Mapped[int] = mapped_column(Numeric(8, 0), default=0)
    refunds: Mapped[float] = mapped_column(Numeric(14, 2), default=0)


class BonusRecord(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "bonus_records"

    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    period: Mapped[str | None] = mapped_column(String(20), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)  # e.g. 招生奖/续费奖/满勤奖
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)

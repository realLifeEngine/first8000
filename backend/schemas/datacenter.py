"""
schemas/datacenter.py
CampusRevenue, BonusRecord schemas, plus computed/reporting response
shapes (ranking, campus rollups) that back the Data Center views —
these are service-layer aggregates, not direct table mirrors.
"""
from __future__ import annotations

from pydantic import ConfigDict
from pydantic import BaseModel

from schemas.common import TimestampOut, PayoutStatus


class CampusRevenueBase(BaseModel):
    period: str
    revenue: float = 0
    new_students: int = 0
    renewals: int = 0
    refunds: float = 0


class CampusRevenueCreate(CampusRevenueBase):
    branch_id: str


class CampusRevenueOut(CampusRevenueBase, TimestampOut):
    id: str
    branch_id: str


class BonusRecordBase(BaseModel):
    user_id: str | None = None
    name: str | None = None
    period: str | None = None
    amount: float = 0
    category: str | None = None
    remark: str | None = None


class BonusRecordCreate(BonusRecordBase):
    branch_id: str


class BonusRecordOut(BonusRecordBase, TimestampOut):
    id: str
    branch_id: str


class RankingRow(BaseModel):
    """Computed leaderboard row — service-layer aggregate, no dedicated table."""
    rank: int
    campus: str
    total_new: int
    renewals: int
    actual_revenue: float


class StaffRankingRow(BaseModel):
    id: str
    name: str
    role: str
    performance: float
    attendance_rate: str
    review_count: int


class BonusSummaryRow(BaseModel):
    id: str
    name: str
    dept: str | None = None
    class_hours: float
    review_bonus: float
    performance_bonus: float
    total_bonus: float
    status: PayoutStatus


class OverviewSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    active_students: int
    monthly_revenue: float
    weekly_attendance_rate: float
    pending_reviews: int

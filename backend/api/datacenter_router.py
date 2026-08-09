"""
api/datacenter_router.py
Data center: CampusRevenue/BonusRecord CRUD, plus computed reporting
endpoints (ranking, staff ranking, bonus summary) built as service-layer
aggregation queries rather than dedicated tables.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_permission
from core.security import Permission, role_at_least
from db.session import get_db
from models.academic import CourseRecord
from models.branch import Branch
from models.datacenter import BonusRecord, CampusRevenue
from models.student import Student
from models.user import User
from schemas.common import PageOut
from schemas.datacenter import (
    BonusRecordCreate, BonusRecordOut, BonusSummaryRow,
    CampusRevenueCreate, CampusRevenueOut, RankingRow, StaffRankingRow,
    OverviewSummary,
)
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/data", tags=["data-center"])

revenue_crud = CRUDBase(CampusRevenue)
bonus_crud = CRUDBase(BonusRecord)


@router.get("/overview-summary", response_model=OverviewSummary)
async def overview_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> OverviewSummary:
    branch_filter = None if role_at_least(user.role, "school_admin") else user.branch_id
    month_period = datetime.now().strftime("%Y-%m")

    students_query = select(
        func.count(Student.id),
        func.coalesce(func.avg(cast(func.replace(func.coalesce(Student.on_time_rate, "0"), "%", ""), Integer)), 0),
    ).where(Student.status.in_(["正常", "停课"]))
    if branch_filter is not None:
        students_query = students_query.where(Student.branch_id == branch_filter)
    active_students, weekly_attendance_rate = (await db.execute(students_query)).one()

    revenue_query = select(func.coalesce(func.sum(CampusRevenue.revenue), 0)).where(CampusRevenue.period == month_period)
    if branch_filter is not None:
        revenue_query = revenue_query.where(CampusRevenue.branch_id == branch_filter)
    monthly_revenue = (await db.execute(revenue_query)).scalar_one()

    review_query = select(func.count(CourseRecord.id)).where(CourseRecord.status == "待评")
    if branch_filter is not None:
        review_query = review_query.where(CourseRecord.branch_id == branch_filter)
    pending_reviews = (await db.execute(review_query)).scalar_one()

    return OverviewSummary(
        active_students=active_students or 0,
        monthly_revenue=float(monthly_revenue or 0),
        weekly_attendance_rate=round(float(weekly_attendance_rate or 0), 1),
        pending_reviews=pending_reviews or 0,
    )


@router.get("/revenue", response_model=PageOut)
async def list_revenue(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.REVENUE_VIEW.value))) -> PageOut:
    items, total = await revenue_crud.list(db, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[CampusRevenueOut.model_validate(i) for i in items])


@router.post("/revenue", response_model=CampusRevenueOut, status_code=201)
async def create_revenue(payload: CampusRevenueCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.REVENUE_VIEW.value))) -> CampusRevenueOut:
    return CampusRevenueOut.model_validate(await revenue_crud.create(db, payload.model_dump()))


@router.get("/bonus", response_model=PageOut)
async def list_bonus(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.BONUS_MANAGE.value))) -> PageOut:
    items, total = await bonus_crud.list(db, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[BonusRecordOut.model_validate(i) for i in items])


@router.post("/bonus", response_model=BonusRecordOut, status_code=201)
async def create_bonus(payload: BonusRecordCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.BONUS_MANAGE.value))) -> BonusRecordOut:
    return BonusRecordOut.model_validate(await bonus_crud.create(db, payload.model_dump()))


@router.get("/ranking", response_model=list[RankingRow])
async def campus_ranking(db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CAMPUS_DATA_VIEW.value))) -> list[RankingRow]:
    """Aggregates CampusRevenue by branch, ranked by actual revenue descending."""
    query = (
        select(
            Branch.name.label("campus"),
            func.sum(CampusRevenue.new_students).label("total_new"),
            func.sum(CampusRevenue.renewals).label("renewals"),
            func.sum(CampusRevenue.revenue).label("actual_revenue"),
        )
        .join(CampusRevenue, CampusRevenue.branch_id == Branch.id)
        .group_by(Branch.id)
        .order_by(func.sum(CampusRevenue.revenue).desc())
    )
    rows = (await db.execute(query)).all()
    return [
        RankingRow(rank=i + 1, campus=r.campus, total_new=r.total_new or 0, renewals=r.renewals or 0, actual_revenue=float(r.actual_revenue or 0))
        for i, r in enumerate(rows)
    ]


@router.get("/staff-ranking", response_model=list[StaffRankingRow])
async def staff_ranking(db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CAMPUS_DATA_VIEW.value))) -> list[StaffRankingRow]:
    """Aggregates bonus amount per staff member as a performance proxy, ranked descending."""
    query = (
        select(User.id, User.nickname, User.role, func.coalesce(func.sum(BonusRecord.amount), 0).label("performance"))
        .outerjoin(BonusRecord, BonusRecord.user_id == User.id)
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(BonusRecord.amount), 0).desc())
    )
    rows = (await db.execute(query)).all()
    return [
        StaffRankingRow(id=r.id, name=r.nickname or "", role=r.role, performance=float(r.performance), attendance_rate="-", review_count=0)
        for r in rows
    ]


@router.get("/bonus-summary", response_model=list[BonusSummaryRow])
async def bonus_summary(db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.BONUS_MANAGE.value))) -> list[BonusSummaryRow]:
    """Per-staff bonus rollup: split into review-tagged vs performance-tagged categories."""
    query = select(User.id, User.nickname, User.dept, BonusRecord.category, BonusRecord.amount).join(BonusRecord, BonusRecord.user_id == User.id)
    rows = (await db.execute(query)).all()
    summary: dict[str, dict] = {}
    for r in rows:
        entry = summary.setdefault(r.id, {"id": r.id, "name": r.nickname or "", "dept": r.dept, "review_bonus": 0.0, "performance_bonus": 0.0})
        if r.category == "招生奖":
            entry["review_bonus"] += float(r.amount)
        else:
            entry["performance_bonus"] += float(r.amount)
    return [
        BonusSummaryRow(
            id=e["id"], name=e["name"], dept=e["dept"], class_hours=0,
            review_bonus=e["review_bonus"], performance_bonus=e["performance_bonus"],
            total_bonus=e["review_bonus"] + e["performance_bonus"], status="待发放",
        )
        for e in summary.values()
    ]

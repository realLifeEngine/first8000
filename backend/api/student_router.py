"""
api/student_router.py
Front-desk member management CRUD — powers MemberList.vue. Field names
in schemas use camelCase aliases so responses match the frontend as-is.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException, status
from sqlalchemy import Integer, case, cast, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_permission
from core.security import role_at_least
from core.security import Permission
from db.session import get_db
from models.academic import ClassStudentMembership, SchoolClass
from models.deleted_student import DeletedStudent
from models.student import Student
from models.user import User
from schemas.common import PageOut
from schemas.student import DeletedStudentOut, StudentClassOptionOut, StudentCreate, StudentOut, StudentPageOut, StudentUpdate
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/students", tags=["students"])
crud = CRUDBase(Student)

ACTIVE_STUDENT_STATUSES = ["意向", "正常", "停课"]


def _apply_student_filters(
    query,
    *,
    branch_filter: str | None,
    search: str | None,
    name: str | None,
    business_status: str | None,
    class_info: str | None,
    counselor: str | None,
):
    if branch_filter is not None:
        query = query.where(Student.branch_id == branch_filter)
    if search:
        search_text = search.strip()
        query = query.where(
            or_(
                Student.name.ilike(f"%{search_text}%"),
                Student.phone.ilike(f"%{search_text}%"),
            )
        )
    if name:
        name_text = name.strip()
        query = query.where(
            or_(
                Student.name.ilike(f"%{name_text}%"),
                Student.phone.ilike(f"%{name_text}%"),
            )
        )
    if business_status and business_status != "全部":
        query = query.where(Student.status == business_status)
    if class_info:
        query = query.where(Student.class_info.ilike(f"%{class_info.strip()}%"))
    if counselor:
        query = query.where(Student.counselor.ilike(f"%{counselor.strip()}%"))
    return query


def _student_order_by(sort_field: str | None, sort_order: int | None):
    direction = desc if sort_order == -1 else lambda column: column
    sort_map = {
        "name": Student.name,
        "gender": Student.gender,
        "age": Student.age,
        "status": Student.status,
        "classInfo": Student.class_info,
        "totalPaid": Student.total_paid,
        "consumed": Student.consumed,
        "counselor": Student.counselor,
    }
    if sort_field == "onTimeRate":
        rate_value = cast(func.replace(func.coalesce(Student.on_time_rate, "0"), "%", ""), Integer)
        return desc(rate_value) if sort_order == -1 else rate_value
    if sort_field in sort_map:
        return direction(sort_map[sort_field])
    return desc(Student.created_at)


def _to_deleted_student_payload(student: Student) -> dict:
    return {
        "original_student_id": student.id,
        "branch_id": student.branch_id,
        "name": student.name,
        "gender": student.gender,
        "age": student.age,
        "status": student.status,
        "class_info": student.class_info,
        "phone": student.phone,
        "remark": student.remark,
        "counselor": student.counselor,
        "total_paid": student.total_paid,
        "stored": student.stored,
        "regular_hours": student.regular_hours,
        "gift_hours": student.gift_hours,
        "other_hours": student.other_hours,
        "consumed": student.consumed,
        "absence": student.absence,
        "on_time_rate": student.on_time_rate,
        "last_consume": student.last_consume,
        "consume_freq": student.consume_freq,
        "last_contact": student.last_contact,
        "next_contact": student.next_contact,
        "review_views": student.review_views,
        "view_rate": student.view_rate,
        "student_created_at": student.created_at,
        "student_updated_at": student.updated_at,
    }


def _to_student_payload(archived: DeletedStudent) -> dict:
    return {
        "branch_id": archived.branch_id,
        "name": archived.name,
        "gender": archived.gender,
        "age": archived.age,
        "status": archived.status,
        "class_info": archived.class_info,
        "phone": archived.phone,
        "remark": archived.remark,
        "counselor": archived.counselor,
        "total_paid": archived.total_paid,
        "stored": archived.stored,
        "regular_hours": archived.regular_hours,
        "gift_hours": archived.gift_hours,
        "other_hours": archived.other_hours,
        "consumed": archived.consumed,
        "absence": archived.absence,
        "on_time_rate": archived.on_time_rate,
        "last_consume": archived.last_consume,
        "consume_freq": archived.consume_freq,
        "last_contact": archived.last_contact,
        "next_contact": archived.next_contact,
        "review_views": archived.review_views,
        "view_rate": archived.view_rate,
    }


async def _sync_class_enrolled(db: AsyncSession, class_id: str | None) -> None:
    if not class_id:
        return
    school_class = await db.get(SchoolClass, class_id)
    if school_class is None:
        return
    enrolled = (
        await db.execute(
            select(func.count())
            .select_from(ClassStudentMembership)
            .where(ClassStudentMembership.class_id == class_id)
        )
    ).scalar_one()
    school_class.enrolled = int(enrolled)


async def _set_student_class_membership(
    db: AsyncSession,
    *,
    student: Student,
    class_id: str | None,
    clear_when_none: bool,
) -> None:
    membership = (
        await db.execute(
            select(ClassStudentMembership)
            .where(ClassStudentMembership.student_id == student.id)
            .limit(1)
        )
    ).scalar_one_or_none()
    previous_class_id = membership.class_id if membership else None

    if class_id:
        school_class = await db.get(SchoolClass, class_id)
        if school_class is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SchoolClass not found")
        if school_class.branch_id != student.branch_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student and class must belong to the same branch")

        if membership is None:
            db.add(
                ClassStudentMembership(
                    class_id=school_class.id,
                    student_id=student.id,
                    branch_id=school_class.branch_id,
                )
            )
        else:
            membership.class_id = school_class.id
            membership.branch_id = school_class.branch_id

        student.class_info = school_class.name
        await _sync_class_enrolled(db, school_class.id)
        if previous_class_id and previous_class_id != school_class.id:
            await _sync_class_enrolled(db, previous_class_id)
        return

    if not clear_when_none:
        return

    if membership is not None:
        await db.delete(membership)
        await _sync_class_enrolled(db, previous_class_id)
    student.class_info = None


@router.get("", response_model=StudentPageOut)
async def list_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    name: str | None = Query(None),
    business_status: str | None = Query(None, alias="status"),
    class_info: str | None = Query(None, alias="classInfo"),
    counselor: str | None = Query(None),
    sort_field: str | None = Query(None, alias="sortField"),
    sort_order: int | None = Query(None, alias="sortOrder"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.STUDENT_VIEW.value)),
) -> StudentPageOut:
    branch_filter = None if role_at_least(user.role, "school_admin") else user.branch_id
    items_query = _apply_student_filters(
        select(Student),
        branch_filter=branch_filter,
        search=search,
        name=name,
        business_status=business_status,
        class_info=class_info,
        counselor=counselor,
    )
    summary_query = _apply_student_filters(
        select(
            func.count(Student.id),
            func.coalesce(func.sum(case((Student.status.in_(ACTIVE_STUDENT_STATUSES), 1), else_=0)), 0),
            func.coalesce(
                func.sum(
                    case(
                        (
                            cast(func.replace(func.coalesce(Student.on_time_rate, "0"), "%", ""), Integer) >= 85,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(func.sum(Student.total_paid), 0),
        ),
        branch_filter=branch_filter,
        search=search,
        name=name,
        business_status=business_status,
        class_info=class_info,
        counselor=counselor,
    )
    total, active, on_time, revenue = (await db.execute(summary_query)).one()
    items = (
        (
            await db.execute(
                items_query.order_by(_student_order_by(sort_field, sort_order)).offset((page - 1) * page_size).limit(page_size)
            )
        )
        .scalars()
        .all()
    )
    return StudentPageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[StudentOut.model_validate(i) for i in items],
        summary={"total": total, "active": active, "on_time": on_time, "revenue": float(revenue or 0)},
    )


@router.get("/public-field", response_model=PageOut)
async def list_public_field_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.STUDENT_VIEW.value)),
) -> PageOut:
    branch_filter = None if role_at_least(user.role, "school_admin") else user.branch_id
    query = select(DeletedStudent)
    count_query = select(func.count()).select_from(DeletedStudent)
    if branch_filter is not None:
        query = query.where(DeletedStudent.branch_id == branch_filter)
        count_query = count_query.where(DeletedStudent.branch_id == branch_filter)
    total = (await db.execute(count_query)).scalar_one()
    items = (
        (
            await db.execute(
                query.order_by(desc(DeletedStudent.deleted_at)).offset((page - 1) * page_size).limit(page_size)
            )
        )
        .scalars()
        .all()
    )
    return PageOut(
        total=total,
        page=page,
        page_size=page_size,
        items=[DeletedStudentOut.model_validate(i).model_dump(by_alias=True) for i in items],
    )


@router.post("/public-field/{deleted_id}/restore", response_model=StudentOut)
async def restore_public_field_student(
    deleted_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.STUDENT_CREATE.value)),
) -> StudentOut:
    archived = await db.get(DeletedStudent, deleted_id)
    if archived is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DeletedStudent not found")

    restored = Student(**_to_student_payload(archived))
    db.add(restored)
    await db.delete(archived)
    await db.commit()
    await db.refresh(restored)
    return StudentOut.model_validate(restored)


@router.get("/class-options", response_model=list[StudentClassOptionOut])
async def list_student_class_options(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.STUDENT_VIEW.value)),
) -> list[StudentClassOptionOut]:
    branch_filter = None if role_at_least(user.role, "school_admin") else user.branch_id
    query = select(SchoolClass.id, SchoolClass.name, SchoolClass.branch_id)
    if branch_filter is not None:
        query = query.where(SchoolClass.branch_id == branch_filter)
    rows = (await db.execute(query.order_by(SchoolClass.name.asc()))).all()
    return [StudentClassOptionOut(id=row.id, name=row.name, branch_id=row.branch_id) for row in rows]


@router.get("/counselor-options", response_model=list[str])
async def list_student_counselor_options(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.STUDENT_VIEW.value)),
) -> list[str]:
    branch_filter = None if role_at_least(user.role, "school_admin") else user.branch_id

    counselor_names: set[str] = set()

    staff_query = select(User.nickname, User.name).where(User.is_active.is_(True))
    if branch_filter is not None:
        staff_query = staff_query.where(User.branch_id == branch_filter)
    staff_query = staff_query.where((User.dept.ilike("%学管%")) | (User.role == "manager"))
    for nickname, name in (await db.execute(staff_query)).all():
        display_name = (nickname or name or "").strip()
        if display_name:
            counselor_names.add(display_name)

    history_query = select(Student.counselor).where(Student.counselor.is_not(None)).where(Student.counselor != "")
    if branch_filter is not None:
        history_query = history_query.where(Student.branch_id == branch_filter)
    for counselor in (await db.execute(history_query)).scalars().all():
        display_name = (counselor or "").strip()
        if display_name:
            counselor_names.add(display_name)

    if not counselor_names:
        fallback_query = select(User.nickname, User.name).where(User.is_active.is_(True))
        if branch_filter is not None:
            fallback_query = fallback_query.where(User.branch_id == branch_filter)
        for nickname, name in (await db.execute(fallback_query)).all():
            display_name = (nickname or name or "").strip()
            if display_name:
                counselor_names.add(display_name)

    return sorted(counselor_names)


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(student_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_VIEW.value))) -> StudentOut:
    return StudentOut.model_validate(await crud.get(db, student_id))


@router.post("", response_model=StudentOut, status_code=201)
async def create_student(payload: StudentCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_CREATE.value))) -> StudentOut:
    data = payload.model_dump(by_alias=False)
    class_id = data.pop("class_id", None)

    student = Student(**data)
    db.add(student)
    await db.flush()

    if class_id is not None:
        await _set_student_class_membership(db, student=student, class_id=class_id, clear_when_none=False)

    await db.commit()
    await db.refresh(student)
    return StudentOut.model_validate(student)


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(student_id: str, payload: StudentUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_EDIT.value))) -> StudentOut:
    data = payload.model_dump(exclude_unset=True, by_alias=False)
    class_id_provided = "class_id" in data
    class_id = data.pop("class_id", None)
    if class_id_provided:
        data.pop("class_info", None)
    if "gender" in data and hasattr(data["gender"], "value"):
        data["gender"] = data["gender"].value
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value

    student = await crud.get(db, student_id)
    for key, value in data.items():
        if value is not None:
            setattr(student, key, value)

    if class_id_provided:
        await _set_student_class_membership(db, student=student, class_id=class_id, clear_when_none=True)

    await db.commit()
    await db.refresh(student)
    return StudentOut.model_validate(student)


@router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_DELETE.value))) -> None:
    student = await crud.get(db, student_id)
    deleted_row = DeletedStudent(**_to_deleted_student_payload(student))
    db.add(deleted_row)
    await db.delete(student)
    await db.commit()

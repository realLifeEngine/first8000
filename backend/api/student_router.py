"""
api/student_router.py
Front-desk member management CRUD — powers MemberList.vue. Field names
in schemas use camelCase aliases so responses match the frontend as-is.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_permission
from core.security import role_at_least
from core.security import Permission
from db.session import get_db
from models.student import Student
from models.user import User
from schemas.common import PageOut
from schemas.student import StudentCreate, StudentOut, StudentUpdate
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/students", tags=["students"])
crud = CRUDBase(Student)


@router.get("", response_model=PageOut)
async def list_students(
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.STUDENT_VIEW.value)),
) -> PageOut:
    branch_filter = None if role_at_least(user.role, "school_admin") else user.branch_id
    items, total = await crud.list(db, branch_id=branch_filter, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[StudentOut.model_validate(i).model_dump(by_alias=True) for i in items])


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(student_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_VIEW.value))) -> StudentOut:
    return StudentOut.model_validate(await crud.get(db, student_id))


@router.post("", response_model=StudentOut, status_code=201)
async def create_student(payload: StudentCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_CREATE.value))) -> StudentOut:
    return StudentOut.model_validate(await crud.create(db, payload.model_dump(by_alias=False)))


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(student_id: str, payload: StudentUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_EDIT.value))) -> StudentOut:
    data = payload.model_dump(exclude_unset=True, by_alias=False)
    if "gender" in data and hasattr(data["gender"], "value"):
        data["gender"] = data["gender"].value
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value
    return StudentOut.model_validate(await crud.update(db, student_id, data))


@router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.STUDENT_DELETE.value))) -> None:
    await crud.delete(db, student_id)

"""
api/staff_router.py
Staff (User) CRUD + StaffPermission grant/revoke — the school_admin-only
permission override workflow from Batch 1/4.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_role
from core.security import hash_password, Permission
from db.session import get_db
from models.user import User
from schemas.common import PageOut
from schemas.user import StaffPermissionSet, UserCreate, UserOut, UserUpdate
from services.auth_service import resolve_permissions, set_staff_permission
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/staff", tags=["staff"])
crud = CRUDBase(User)


@router.get("", response_model=PageOut)
async def list_staff(
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_active_user),
) -> PageOut:
    from core.security import role_at_least
    branch_filter = None if role_at_least(user.role, "school_admin") else user.branch_id
    items, total = await crud.list(db, branch_id=branch_filter, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[UserOut.model_validate(i) for i in items])


@router.get("/{staff_id}", response_model=UserOut)
async def get_staff(staff_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> UserOut:
    return UserOut.model_validate(await crud.get(db, staff_id))


@router.post("", response_model=UserOut, status_code=201)
async def create_staff(payload: UserCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("school_admin"))) -> UserOut:
    data = payload.model_dump()
    password = data.pop("password")
    data["hashed_password"] = hash_password(password)
    data["role"] = data["role"].value if hasattr(data["role"], "value") else data["role"]
    return UserOut.model_validate(await crud.create(db, data))


@router.put("/{staff_id}", response_model=UserOut)
async def update_staff(staff_id: str, payload: UserUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_role("manager"))) -> UserOut:
    data = payload.model_dump(exclude_unset=True)
    if "role" in data and hasattr(data["role"], "value"):
        data["role"] = data["role"].value
    return UserOut.model_validate(await crud.update(db, staff_id, data))


@router.delete("/{staff_id}", status_code=204)
async def delete_staff(staff_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_role("school_admin"))) -> None:
    await crud.delete(db, staff_id)


@router.get("/{staff_id}/permissions", response_model=list[str])
async def get_staff_permissions(staff_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> list[str]:
    target = await crud.get(db, staff_id)
    return sorted(await resolve_permissions(db, target))


@router.post("/{staff_id}/permissions", status_code=200)
async def set_staff_permission_route(
    staff_id: str, payload: StaffPermissionSet,
    db: AsyncSession = Depends(get_db), admin: User = Depends(require_role("school_admin")),
) -> dict:
    valid_keys = {p.value for p in Permission}
    if payload.permission_key not in valid_keys:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown permission key")
    await set_staff_permission(db, staff_id, payload.permission_key, payload.is_granted, admin.id)
    return {"ok": True}

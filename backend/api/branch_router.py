"""api/branch_router.py — Branch (campus) CRUD. Creation restricted to superuser."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_role
from db.session import get_db
from models.branch import Branch
from schemas.branch import BranchCreate, BranchOut, BranchUpdate
from schemas.common import PageOut
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/branches", tags=["branches"])
crud = CRUDBase(Branch)


@router.get("", response_model=PageOut)
async def list_branches(
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user),
) -> PageOut:
    items, total = await crud.list(db, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[BranchOut.model_validate(i) for i in items])


@router.get("/{branch_id}", response_model=BranchOut)
async def get_branch(branch_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> BranchOut:
    return BranchOut.model_validate(await crud.get(db, branch_id))


@router.post("", response_model=BranchOut, status_code=201)
async def create_branch(payload: BranchCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("superuser"))) -> BranchOut:
    return BranchOut.model_validate(await crud.create(db, payload.model_dump()))


@router.put("/{branch_id}", response_model=BranchOut)
async def update_branch(branch_id: str, payload: BranchUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_role("superuser"))) -> BranchOut:
    return BranchOut.model_validate(await crud.update(db, branch_id, payload.model_dump(exclude_unset=True)))


@router.delete("/{branch_id}", status_code=204)
async def delete_branch(branch_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_role("superuser"))) -> None:
    await crud.delete(db, branch_id)

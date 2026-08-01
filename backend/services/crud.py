"""
services/crud.py
Generic async CRUD helper to avoid repeating boilerplate across the many
1:1 model<->schema routers in api/. Each router still defines its own
Pydantic schemas and permission requirements; this only handles the
repetitive DB plumbing (list/get/create/update/delete + branch scoping
+ pagination).
"""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import Base

ModelT = TypeVar("ModelT", bound=Base)


class CRUDBase(Generic[ModelT]):
    def __init__(self, model: type[ModelT]):
        self.model = model

    async def get(self, db: AsyncSession, id_: str) -> ModelT:
        obj = await db.get(self.model, id_)
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found")
        return obj

    async def list(
        self,
        db: AsyncSession,
        branch_id: str | None = None,
        page: int = 1,
        page_size: int = 10,
        order_by: Any = None,
    ) -> tuple[list[ModelT], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)
        if branch_id is not None and hasattr(self.model, "branch_id"):
            query = query.where(self.model.branch_id == branch_id)
            count_query = count_query.where(self.model.branch_id == branch_id)
        if order_by is not None:
            query = query.order_by(order_by)
        total = (await db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        items = (await db.execute(query)).scalars().all()
        return list(items), total

    async def create(self, db: AsyncSession, data: dict) -> ModelT:
        obj = self.model(**data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, id_: str, data: dict) -> ModelT:
        obj = await self.get(db, id_)
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id_: str) -> None:
        obj = await self.get(db, id_)
        await db.delete(obj)
        await db.commit()

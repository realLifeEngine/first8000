"""schemas/branch.py — Branch (campus) create/update/out schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.common import ORMBase, TimestampOut


class BranchBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=30)
    address: str | None = None
    phone: str | None = None
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class BranchOut(BranchBase, TimestampOut):
    id: str

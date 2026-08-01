"""schemas/user.py — User (staff) + StaffPermission schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from schemas.common import ORMBase, TimestampOut, Role


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    name: str = Field(min_length=1, max_length=60)
    nickname: str | None = None
    phone: str | None = None
    dept: str | None = None
    role: Role = Role.TEACHER
    branch_id: str
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = None
    nickname: str | None = None
    phone: str | None = None
    dept: str | None = None
    role: Role | None = None
    is_active: bool | None = None


class UserOut(UserBase, TimestampOut):
    id: str
    last_login_at: datetime | None = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)


class StaffPermissionSet(BaseModel):
    """Payload for school_admin/superuser to grant or revoke a permission key."""
    permission_key: str
    is_granted: bool


class StaffPermissionOut(ORMBase):
    id: str
    user_id: str
    permission_key: str
    is_granted: bool
    granted_by_id: str | None = None

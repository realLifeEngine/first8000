"""
models/user.py
User (staff accounts, branch-scoped) + StaffPermission (per-user
permission grant/revoke overrides layered on top of role defaults).
"""
from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from models.base import UUIDPKMixin, TimestampMixin, BranchScopedMixin


class User(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(60), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dept: Mapped[str | None] = mapped_column(String(60), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="teacher")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)

    branch: Mapped["Branch"] = relationship(back_populates="users")
    permission_grants: Mapped[list["StaffPermission"]] = relationship(back_populates="user", cascade="all, delete-orphan", foreign_keys="[StaffPermission.user_id]")


class StaffPermission(Base, UUIDPKMixin, TimestampMixin):
    """
    Per-user override on top of DEFAULT_ROLE_PERMISSIONS.
    is_granted=True  -> explicitly grants a permission the role lacks by default.
    is_granted=False -> explicitly revokes a permission the role has by default.
    Granted/revoked only by school_admin or superuser (enforced in Batch 4).
    """
    __tablename__ = "staff_permissions"
    __table_args__ = (UniqueConstraint("user_id", "permission_key", name="uq_user_permission"),)

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    permission_key: Mapped[str] = mapped_column(String(60), nullable=False)
    is_granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    granted_by_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    user: Mapped["User"] = relationship(back_populates="permission_grants", foreign_keys="[StaffPermission.user_id]")

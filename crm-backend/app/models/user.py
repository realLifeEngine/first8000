"""
User (staff) account and per-staff permission overrides.

Roles:
  superuser     — global, can create branches and manage all data
  school_admin  — full access within own branch; can grant permissions
  manager       — medium privilege within own branch
  teacher       — minimum teacher-related features within own branch
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.branch import Branch


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(120))
    # teacher | manager | school_admin | superuser
    role: Mapped[str] = mapped_column(String(32), index=True)
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    branch: Mapped["Branch"] = relationship(back_populates="users")
    permissions: Mapped[list["StaffPermission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="StaffPermission.user_id",
    )


class StaffPermission(Base):
    """Individual permission grant — school_admin fine-tunes access per staff."""
    __tablename__ = "staff_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    permission_key: Mapped[str] = mapped_column(String(64), index=True)
    granted_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(
        back_populates="permissions", foreign_keys=[user_id]
    )

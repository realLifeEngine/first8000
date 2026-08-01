"""
services/auth_service.py
Auth business logic: credential verification, account lockout, token
issuance, and effective-permission resolution (role defaults + per-user
StaffPermission overrides).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.logging_config import audit_event, get_logger
from core.security import (
    DEFAULT_ROLE_PERMISSIONS,
    Role,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from models.user import StaffPermission, User

logger = get_logger(__name__)


class AuthError(Exception):
    """Base auth exception; message is safe to return to the client."""


class InvalidCredentialsError(AuthError):
    pass


class AccountLockedError(AuthError):
    def __init__(self, unlock_at: datetime):
        self.unlock_at = unlock_at
        super().__init__(f"Account locked until {unlock_at.isoformat()}")


class AccountInactiveError(AuthError):
    pass


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def _is_locked(user: User) -> bool:
    return bool(user.locked_until and user.locked_until > datetime.now(timezone.utc))


async def resolve_permissions(db: AsyncSession, user: User) -> set[str]:
    """Effective permissions = role defaults, with per-user grants/revokes layered on top."""
    try:
        role_enum = Role(user.role)
        effective = {p.value for p in DEFAULT_ROLE_PERMISSIONS.get(role_enum, set())}
    except ValueError:
        effective = set()

    result = await db.execute(select(StaffPermission).where(StaffPermission.user_id == user.id))
    overrides = result.scalars().all()
    for grant in overrides:
        if grant.is_granted:
            effective.add(grant.permission_key)
        else:
            effective.discard(grant.permission_key)
    return effective


async def authenticate(db: AsyncSession, username: str, password: str, ip: str | None = None) -> User:
    """
    Verifies credentials, enforcing the lockout policy from core.config:
    LOGIN_MAX_ATTEMPTS failed attempts within tracking triggers a
    LOGIN_LOCKOUT_MINUTES lockout window.
    """
    user = await get_user_by_username(db, username)

    if user is None:
        # Constant-time-ish: still hash to avoid trivial username enumeration via timing.
        hash_password(password)
        audit_event("login_failed_unknown_user", target_id=None, username=username, ip=ip)
        raise InvalidCredentialsError("Invalid username or password")

    if not user.is_active:
        audit_event("login_failed_inactive", actor_id=user.id, ip=ip)
        raise AccountInactiveError("Account is disabled")

    if _is_locked(user):
        audit_event("login_blocked_locked", actor_id=user.id, ip=ip, locked_until=user.locked_until.isoformat())
        raise AccountLockedError(user.locked_until)

    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
            user.failed_login_attempts = 0
            audit_event("account_locked", actor_id=user.id, ip=ip, lockout_minutes=settings.LOGIN_LOCKOUT_MINUTES)
        await db.commit()
        audit_event("login_failed_bad_password", actor_id=user.id, ip=ip)
        raise InvalidCredentialsError("Invalid username or password")

    # Success: reset failure counters, stamp last login.
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    audit_event("login_success", actor_id=user.id, ip=ip)
    return user


async def issue_tokens(user: User) -> tuple[str, str]:
    access = create_access_token(user_id=user.id, role=user.role, branch_id=user.branch_id)
    refresh = create_refresh_token(user_id=user.id)
    return access, refresh


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise InvalidCredentialsError("Not a refresh token")
    user = await get_user_by_id(db, payload["sub"])
    if user is None or not user.is_active:
        raise InvalidCredentialsError("User no longer valid")
    audit_event("token_refreshed", actor_id=user.id)
    return create_access_token(user_id=user.id, role=user.role, branch_id=user.branch_id)


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.hashed_password):
        raise InvalidCredentialsError("Old password is incorrect")
    user.hashed_password = hash_password(new_password)
    await db.commit()
    audit_event("password_changed", actor_id=user.id)


async def set_staff_permission(db: AsyncSession, target_user_id: str, permission_key: str, is_granted: bool, granted_by_id: str) -> StaffPermission:
    """Upsert a permission override row. Only callable by school_admin/superuser (enforced at API layer)."""
    result = await db.execute(
        select(StaffPermission).where(
            StaffPermission.user_id == target_user_id,
            StaffPermission.permission_key == permission_key,
        )
    )
    grant = result.scalar_one_or_none()
    if grant is None:
        grant = StaffPermission(
            user_id=target_user_id, permission_key=permission_key,
            is_granted=is_granted, granted_by_id=granted_by_id,
        )
        db.add(grant)
    else:
        grant.is_granted = is_granted
        grant.granted_by_id = granted_by_id
    await db.commit()
    await db.refresh(grant)
    audit_event(
        "permission_granted" if is_granted else "permission_revoked",
        actor_id=granted_by_id, target_id=target_user_id, permission_key=permission_key,
    )
    return grant

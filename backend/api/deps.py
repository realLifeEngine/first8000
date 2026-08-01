"""
api/deps.py
FastAPI dependency guards: current-user extraction from JWT, minimum-role
enforcement, and granular permission checks (role defaults + StaffPermission
overrides). Also enforces branch scoping so staff can't cross campuses
unless they're school_admin/superuser.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import role_at_least, decode_token
from db.session import get_db
from models.user import User
from services.auth_service import get_user_by_id, resolve_permissions

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_error
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_error
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    return user


def require_role(minimum_role: str):
    """Dependency factory: require the caller's role to be >= minimum_role in the hierarchy."""
    async def _checker(user: User = Depends(get_current_active_user)) -> User:
        if not role_at_least(user.role, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role >= {minimum_role}",
            )
        return user
    return _checker


def require_permission(permission_key: str):
    """Dependency factory: require an effective granular permission (role default + overrides)."""
    async def _checker(
        user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        effective = await resolve_permissions(db, user)
        if permission_key not in effective:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_key}",
            )
        return user
    return _checker


def require_same_branch_or_admin(branch_id: str):
    """Dependency factory: restrict access to the user's own branch unless school_admin+."""
    async def _checker(user: User = Depends(get_current_active_user)) -> User:
        if role_at_least(user.role, "school_admin"):
            return user
        if user.branch_id != branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cross-branch access denied",
            )
        return user
    return _checker

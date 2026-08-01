"""
api/auth_router.py
Auth endpoints: login (rate-limited), refresh, current-user info, and
password change. Full router set for all business modules lands in Batch 5;
this router exists now to validate the Batch 4 security stack end-to-end.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user
from core.config import settings
from db.session import get_db
from middleware.rate_limit import limiter
from models.user import User
from schemas.auth import CurrentUser, LoginRequest, RefreshRequest, TokenPair
from schemas.user import PasswordChange
from services.auth_service import (
    AccountInactiveError,
    AccountLockedError,
    InvalidCredentialsError,
    authenticate,
    change_password,
    issue_tokens,
    refresh_access_token,
    resolve_permissions,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    client_ip = request.client.host if request.client else None
    try:
        user = await authenticate(db, payload.username, payload.password, ip=client_ip)
    except AccountLockedError as e:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(e))
    except AccountInactiveError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    access, refresh = await issue_tokens(user)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    try:
        new_access = await refresh_access_token(db, payload.refresh_token)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenPair(access_token=new_access, refresh_token=payload.refresh_token)


@router.get("/me", response_model=CurrentUser)
async def me(user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> CurrentUser:
    perms = await resolve_permissions(db, user)
    return CurrentUser(
        id=user.id, username=user.username, name=user.name,
        role=user.role, branch_id=user.branch_id, permissions=sorted(perms),
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password_route(
    payload: PasswordChange,
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await change_password(db, user, payload.old_password, payload.new_password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

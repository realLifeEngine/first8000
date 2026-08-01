"""
schemas/auth.py
Auth request/response schemas: login, token pair, refresh.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.common import Role


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    password: str = Field(min_length=6, max_length=128)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class CurrentUser(BaseModel):
    id: str
    username: str
    name: str
    role: Role
    branch_id: str
    permissions: list[str] = []

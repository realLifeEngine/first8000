"""
core/config.py
Centralized application configuration using Pydantic Settings (v2).
All values are environment-driven with sensible dev defaults so the app
runs out-of-the-box against local SQLite, then swaps to Postgres in prod
by simply changing DATABASE_URL.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "Kaku CRM API"
    APP_ENV: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    # SQLite for local/mock data; swap to postgresql+asyncpg://... in prod via env var.
    DATABASE_URL: str = "sqlite+aiosqlite:///./kaku_crm.db"
    DB_ECHO: bool = False

    # --- JWT / Auth ---
    JWT_SECRET_KEY: str = Field(default="CHANGE_ME_IN_PROD_ENV_FILE")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # --- RBAC ---
    # 4-tier role hierarchy, lowest -> highest privilege.
    ROLE_HIERARCHY: tuple[str, ...] = ("teacher", "manager", "school_admin", "superuser")

    # --- Account lockout / brute force defense ---
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # --- Rate limiting (Redis-backed sliding window via slowapi) ---
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_ENABLED: bool = True

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # --- Pagination defaults ---
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — import and call get_settings() everywhere."""
    return Settings()


settings = get_settings()

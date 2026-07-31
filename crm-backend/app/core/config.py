"""
Application configuration using Pydantic Settings.
All values are overridable via environment variables or a .env file.
"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Qihui Education CRM API")
    environment: str = Field(default="production")
    debug: bool = Field(default=False)

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Database (SQLite async for demo/mock; swap to postgresql+asyncpg for real prod)
    database_url: str = Field(default="sqlite+aiosqlite:///./crm.db")

    # Redis (used for distributed rate limiting / anti-DDoS token buckets)
    redis_url: str = Field(default="redis://localhost:6379/0")
    use_redis: bool = Field(default=False)  # falls back to in-memory limiter if False

    # JWT / Auth
    secret_key: str = Field(default="CHANGE_ME_SUPER_SECRET_KEY_IN_PRODUCTION_ENV")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:4173"]
    )

    # Rate limiting / anti-DDoS
    rate_limit_default: str = Field(default="100/minute")
    rate_limit_login: str = Field(default="5/minute")
    rate_limit_burst_block_seconds: int = Field(default=300)
    max_failed_login_attempts: int = Field(default=5)
    account_lockout_minutes: int = Field(default=15)

    # Bot defense
    honeypot_field_name: str = Field(default="website_url")
    min_form_submit_seconds: float = Field(default=1.2)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

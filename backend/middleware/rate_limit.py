"""
middleware/rate_limit.py
Redis-backed sliding-window rate limiting via slowapi. If Redis is
unreachable at startup, falls back to in-memory storage so the app still
boots (dev/CI convenience) — production deployments should always run
with REDIS_URL set and reachable so limits are shared across workers.
"""
from __future__ import annotations

import redis as redis_lib
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


def _resolve_storage_uri() -> str:
    if not settings.RATE_LIMIT_ENABLED:
        return "memory://"
    try:
        client = redis_lib.from_url(settings.REDIS_URL, socket_connect_timeout=0.5)
        client.ping()
        return settings.REDIS_URL
    except Exception as exc:
        logger.warning(f"Redis unreachable ({exc}); falling back to in-memory rate limit storage")
        return "memory://"


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_resolve_storage_uri(),
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    enabled=settings.RATE_LIMIT_ENABLED,
)

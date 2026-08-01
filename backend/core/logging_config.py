"""
core/logging_config.py
Structured (JSON) application logging + a dedicated security audit logger
used for auth events, permission grants/revokes, and lockouts. Kept
separate from app logs so security review doesn't require grepping
general noise.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from core.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Allow extra structured fields via logging.LoggerAdapter / extra=
        for key, value in record.__dict__.items():
            if key in ("args", "msg", "exc_info", "exc_text", "stack_info") or key in payload:
                continue
            if key.startswith("_"):
                continue
            if key in logging.LogRecord.__dict__:
                continue
            payload[key] = value
        return json.dumps(payload, default=str, ensure_ascii=False)


def _build_handler() -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    return handler


def configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    root.handlers.clear()
    root.addHandler(_build_handler())

    # Quiet down noisy third-party loggers in dev.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


# --------------------------------------------------------------------------
# Security audit logger
# Used for: login success/failure, lockouts, token refresh/revoke,
# permission grant/revoke, role changes, branch creation.
# --------------------------------------------------------------------------
security_audit_logger = logging.getLogger("security.audit")


def audit_event(event: str, actor_id: str | None = None, target_id: str | None = None, **extra: Any) -> None:
    """
    Emit a structured security audit log line.
    Example: audit_event("login_success", actor_id=user.id, ip=request.client.host)
    """
    security_audit_logger.info(
        event,
        extra={"event": event, "actor_id": actor_id, "target_id": target_id, **extra},
    )

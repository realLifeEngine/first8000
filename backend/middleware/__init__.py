"""
middleware package
setup_middleware() wires the full defensive stack onto a FastAPI app in
the order: RequestID -> SecurityHeaders -> Honeypot -> CORS -> rate-limit
exception handler. Called once from main.py's app factory (Batch 6).
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from core.config import settings
from middleware.honeypot import HoneypotMiddleware
from middleware.rate_limit import limiter
from middleware.request_id import RequestIDMiddleware
from middleware.security_headers import SecurityHeadersMiddleware


def setup_middleware(app: FastAPI) -> None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(HoneypotMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

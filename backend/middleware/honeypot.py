"""
middleware/honeypot.py
Bot-trap middleware: exposes a fake endpoint path (e.g. /wp-login.php,
/.env) that legitimate clients never hit. Any request to a honeypot path
is logged as a security event and immediately rejected, and repeat
offenders' IPs can be fed into a blocklist by the caller.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from core.logging_config import audit_event

HONEYPOT_PATHS = {
    "/wp-login.php", "/wp-admin", "/.env", "/.git/config",
    "/admin.php", "/phpmyadmin", "/xmlrpc.php", "/config.json",
}


class HoneypotMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.url.path in HONEYPOT_PATHS:
            audit_event(
                "honeypot_triggered",
                ip=request.client.host if request.client else None,
                path=request.url.path,
                user_agent=request.headers.get("user-agent"),
            )
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        return await call_next(request)

"""
middleware/operation_audit.py
Writes operation audit rows for authenticated mutating API requests.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from core.logging_config import get_logger
from core.security import decode_token
from db.session import AsyncSessionLocal
from models.oa import OperationLog

logger = get_logger(__name__)


class OperationAuditMiddleware(BaseHTTPMiddleware):
    MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)

        if request.method not in self.MUTATION_METHODS:
            return response
        if not request.url.path.startswith("/api/v1/"):
            return response

        auth_header = request.headers.get("authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return response

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
        except Exception:
            return response

        if payload.get("type") != "access":
            return response

        user_id = payload.get("sub")
        branch_id = payload.get("branch_id")
        if not user_id or not branch_id:
            return response

        module = "-"
        parts = request.url.path.split("/")
        if len(parts) >= 4:
            module = parts[3]

        try:
            async with AsyncSessionLocal() as db:
                db.add(
                    OperationLog(
                        user_id=user_id,
                        branch_id=branch_id,
                        action=f"{request.method} {request.url.path}",
                        module=module,
                        ip=request.client.host if request.client else None,
                        detail=f"status={response.status_code}",
                    )
                )
                await db.commit()
        except Exception as exc:
            logger.warning(f"Operation audit log write failed: {exc}")

        return response

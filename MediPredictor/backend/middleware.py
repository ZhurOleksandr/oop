# backend/middleware.py
"""
Custom middleware:
  - RequestTimingMiddleware  — logs response time for every request
  - AuditLogMiddleware       — writes sensitive actions to audit_log table
"""
from __future__ import annotations
import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("medipredictor")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── Request timing ──────────────────────────────────────────────────────────

class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Adds X-Process-Time header and logs slow requests (> 1s)."""

    def __init__(self, app: ASGIApp, slow_threshold_ms: int = 1000):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}ms"

        level = logging.WARNING if elapsed_ms > self.slow_threshold_ms else logging.INFO
        logger.log(
            level,
            "%s %s → %d  [%.1fms]",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response


# ── Security headers ────────────────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds basic security headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-XSS-Protection": "1; mode=block",
        })
        return response


# ── Audit logging ───────────────────────────────────────────────────────────

# Paths that should be audited (method, path-prefix)
_AUDIT_PATHS: list[tuple[str, str]] = [
    ("POST",   "/api/auth/login"),
    ("POST",   "/api/patients"),
    ("DELETE", "/api/patients"),
    ("POST",   "/api/analyses"),
    ("DELETE", "/api/analyses"),
    ("POST",   "/api/algorithms"),
    ("PUT",    "/api/algorithms"),
    ("DELETE", "/api/algorithms"),
    ("POST",   "/api/users"),
    ("PUT",    "/api/users"),
    ("DELETE", "/api/users"),
]

def _should_audit(method: str, path: str) -> bool:
    for m, p in _AUDIT_PATHS:
        if method == m and path.startswith(p):
            return True
    return False


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Logs sensitive write operations to both the Python logger and
    the audit_log DB table (best-effort — never blocks the response).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)

        if not _should_audit(request.method, request.url.path):
            return response

        # Extract user id from JWT (best-effort, no exception propagation)
        user_id: str | None = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from jose import jwt as jose_jwt
                from config import get_settings
                settings = get_settings()
                payload = jose_jwt.decode(
                    auth_header[7:],
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )
                user_id = payload.get("sub")
            except Exception:
                pass

        client_ip = request.client.host if request.client else None

        logger.info(
            "AUDIT  user=%s  %s %s  status=%d  ip=%s",
            user_id or "anonymous",
            request.method,
            request.url.path,
            response.status_code,
            client_ip,
        )

        # Async DB write — fire and forget
        if response.status_code < 400:
            import asyncio
            asyncio.create_task(
                _write_audit_log(
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    ip_address=client_ip,
                )
            )

        return response


async def _write_audit_log(user_id: str | None, action: str, ip_address: str | None):
    """Write one row to audit_log. Silently swallows errors."""
    try:
        from database import AsyncSessionLocal, audit_log  # type: ignore
        from sqlalchemy import insert
        import uuid

        async with AsyncSessionLocal() as session:
            await session.execute(
                insert(audit_log).values(
                    user_id=uuid.UUID(user_id) if user_id else None,
                    action=action,
                    ip_address=ip_address,
                )
            )
            await session.commit()
    except Exception:
        pass  # Never crash the request because of audit logging

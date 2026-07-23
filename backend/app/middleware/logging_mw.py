from datetime import datetime
import json
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                raw = await request.body()
                request.scope["body"] = raw
                body = json.loads(raw) if raw else None
            except Exception:
                body = None

        response = await call_next(request)

        elapsed = time.time() - start
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "elapsed_ms": round(elapsed * 1000, 2),
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
        }
        if body and isinstance(body, dict):
            sanitized = {k: v for k, v in body.items() if k not in ("password", "auth_token", "api_key")}
            log_data["body_preview"] = json.dumps(sanitized)[:200]

        if response.status_code >= 400:
            logger.error("request_failed", **log_data)
        else:
            logger.info("request_ok", **log_data)

        response.headers["X-Response-Time-Ms"] = str(round(elapsed * 1000, 2))
        return response

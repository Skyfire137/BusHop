# app/middleware/api_key.py
import hmac
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings

logger = logging.getLogger(__name__)

EXEMPT_PATHS = {"/health", "/docs", "/docs/oauth2-redirect", "/openapi.json", "/redoc"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)

        api_key = request.headers.get("X-Internal-API-Key")
        if not api_key or not hmac.compare_digest(api_key.encode(), settings.internal_api_key.encode()):
            logger.warning(
                "Unauthorized request to %s (key_present=%s)",
                request.url.path,
                bool(api_key),
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
            )

        return await call_next(request)

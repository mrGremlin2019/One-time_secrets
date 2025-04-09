"""
Middleware, добавляющий заголовки для запрета кеширования на клиенте и прокси.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class NoCacheHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware, добавляющий заголовки no-store / no-cache / expires.
    """
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

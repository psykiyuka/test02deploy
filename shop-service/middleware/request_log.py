import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("shop")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000

        logger.info(
            "%s %s -> %d | %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response
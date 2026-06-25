import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from common.context import request_id_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:8]
        request_id_var.set(request_id)

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        return response
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from common.exceptions import ShopException
from common.context import request_id_var

logger = logging.getLogger("shop")


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ShopException)
    async def shop_exception_handler(request, exc: ShopException):
        logger.warning(
            "业务异常 | code=%s | message=%s | path=%s",
            exc.code,
            exc.message,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id_var.get("-"),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc: Exception):
        logger.error(
            "未预期异常 | type=%s | message=%s | path=%s",
            type(exc).__name__,
            str(exc),
            request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "code": 50002,
                "message": "未预期的内部错误",
                "request_id": request_id_var.get("-"),
            },
        )
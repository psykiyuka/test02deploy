from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# 加载 .env 文件（如果存在）
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common import setup_logger, logger
from infrastructure import (
    init_pool,
    close_pool,
    init_redis,
    close_redis,
    scheduler,
    start_scheduler,
    shutdown_scheduler,
)
from middleware import RequestIDMiddleware, RequestLogMiddleware, register_exception_handlers
from domain.order import cancel_timeout_orders
from apps.c_endpoint.product.router import router as product_router
from apps.c_endpoint.user.router import router as user_router
from apps.c_endpoint.cart.router import router as cart_router
from apps.c_endpoint.order.router import router as order_router
from apps.c_endpoint.logistics.router import router as logistics_router
from apps.c_endpoint.after_sale.router import router as after_sale_router
from apps.c_endpoint.category.router import router as c_category_router
from apps.c_endpoint.favorite.router import router as favorite_router
from apps.c_endpoint.address.router import router as address_router
from apps.b_endpoint.category_router import router as category_router
from apps.b_endpoint.product_router import router as b_product_router
from apps.b_endpoint.order_router import router as b_order_router
from apps.b_endpoint.after_sale_router import router as b_after_sale_router
from apps.b_endpoint.dashboard_router import router as dashboard_router
from apps.b_endpoint.user_router import router as b_user_router
from apps.m_endpoint.router import router as merchant_router
from apps.m_endpoint.ai_chat_router import router as merchant_ai_chat_router
from apps.c_endpoint.ai_chat_router import router as c_ai_chat_router
from apps.admin_endpoint.ai_chat_router import router as admin_ai_chat_router
from apps.c_endpoint.chat_router import router as c_chat_router
from apps.m_endpoint.chat_router import router as m_chat_router
from apps.admin_endpoint.chat_router import router as admin_chat_router
from apps.internal.router import router as internal_router
from apps.c_endpoint.payment.router import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    logger.info("===== shop-service 启动中 =====")

    init_pool()
    init_redis()

    scheduler.add_job(
        cancel_timeout_orders,
        trigger="interval",
        minutes=5,
        id="cancel_timeout_orders",
        name="超时订单自动取消",
    )
    start_scheduler()
    logger.info("===== shop-service 启动完成 =====")

    yield

    logger.info("===== shop-service 关闭中 =====")
    shutdown_scheduler()
    close_redis()
    close_pool()
    logger.info("===== shop-service 已关闭 =====")


app = FastAPI(
    title="电商平台 - Shop Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# 统一前缀 /api/shop（Nginx 在 Docker 环境做路径转发，本地开发需要此前缀）
_prefix = "/api/shop"

app.include_router(user_router,         prefix=_prefix)
app.include_router(product_router,      prefix=_prefix)
app.include_router(cart_router,         prefix=_prefix)
app.include_router(order_router,        prefix=_prefix)
app.include_router(logistics_router,    prefix=_prefix)
app.include_router(after_sale_router,   prefix=_prefix)
app.include_router(c_category_router,   prefix=_prefix)
app.include_router(favorite_router,     prefix=_prefix)
app.include_router(address_router,      prefix=_prefix)
app.include_router(category_router,     prefix=_prefix)
app.include_router(b_product_router,    prefix=_prefix)
app.include_router(b_order_router,      prefix=_prefix)
app.include_router(b_after_sale_router, prefix=_prefix)
app.include_router(dashboard_router,    prefix=_prefix)
app.include_router(b_user_router,       prefix=_prefix)
app.include_router(merchant_router,     prefix=_prefix)
app.include_router(merchant_ai_chat_router, prefix=_prefix)
app.include_router(c_ai_chat_router, prefix=_prefix)
app.include_router(admin_ai_chat_router, prefix=_prefix)
app.include_router(c_chat_router, prefix=_prefix)
app.include_router(m_chat_router, prefix=_prefix)
app.include_router(admin_chat_router, prefix=_prefix)
app.include_router(internal_router,     prefix=_prefix)
app.include_router(payment_router,     prefix=_prefix)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "shop-service"}
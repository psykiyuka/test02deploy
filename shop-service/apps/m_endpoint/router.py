from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from apps.common.auth import get_current_merchant
from domain.product import create_product, update_product, toggle_product_status, get_products_by_merchant, get_product_detail
from domain.order import get_orders_by_merchant, update_logistics_status
from domain.after_sale import get_after_sales_by_merchant, approve_after_sale, reject_after_sale, complete_after_sale, confirm_return_received, resend_exchange
from apps.c_endpoint.product.schema import CreateProductRequest, UpdateProductRequest, ToggleStatusRequest
from apps.c_endpoint.logistics.schema import UpdateLogisticsRequest

router = APIRouter(prefix="/m-endpoint", tags=["M端-商家"])


@router.get("/products")
def m_get_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_merchant),
):
    result = get_products_by_merchant(user["user_id"], page, size)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/products/{product_id}")
def m_get_product(product_id: int, user: dict = Depends(get_current_merchant)):
    product = get_product_detail(product_id, check_status=False)
    return {"code": 0, "data": product, "message": "success"}


@router.post("/products")
def m_create_product(req: CreateProductRequest, user: dict = Depends(get_current_merchant)):
    result = create_product(
        req.name,
        req.description,
        req.price,
        req.image_url,
        req.stock,
        req.category_id,
        user["user_id"],
    )
    return {"code": 0, "data": result, "message": "创建成功，请等待审核"}


@router.put("/products/{product_id}")
def m_update_product(product_id: int, req: UpdateProductRequest, user: dict = Depends(get_current_merchant)):
    result = update_product(
        product_id,
        name=req.name,
        description=req.description,
        price=req.price,
        image_url=req.image_url,
        stock=req.stock,
        category_id=req.category_id,
    )
    return {"code": 0, "data": result, "message": "success"}


@router.put("/products/{product_id}/status")
def m_toggle_product_status(product_id: int, req: ToggleStatusRequest, user: dict = Depends(get_current_merchant)):
    result = toggle_product_status(product_id, req.status)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/orders")
def m_get_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_merchant),
):
    result = get_orders_by_merchant(user["user_id"], page, size)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/orders/{order_id}/logistics")
def m_update_logistics(order_id: int, req: UpdateLogisticsRequest, user: dict = Depends(get_current_merchant)):
    result = update_logistics_status(order_id, req.status, req.tracking_number, user["user_id"])
    return {"code": 0, "data": result, "message": "success"}


# ── M 端售后管理 ──

@router.get("/after-sales")
def m_get_after_sales(
    status: str = Query(None),
    page: int = Query(1),
    size: int = Query(20),
    user: dict = Depends(get_current_merchant),
):
    result = get_after_sales_by_merchant(merchant_id=user["user_id"], status=status, page=page, size=size)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/after-sales/{after_sale_id}/approve")
def m_approve_after_sale(after_sale_id: int, user: dict = Depends(get_current_merchant)):
    result = approve_after_sale(after_sale_id, merchant_id=user["user_id"])
    return {"code": 0, "data": result, "message": "success"}


@router.put("/after-sales/{after_sale_id}/reject")
def m_reject_after_sale(after_sale_id: int, user: dict = Depends(get_current_merchant)):
    result = reject_after_sale(after_sale_id, merchant_id=user["user_id"])
    return {"code": 0, "data": result, "message": "success"}


@router.put("/after-sales/{after_sale_id}/complete")
def m_complete_after_sale(after_sale_id: int, user: dict = Depends(get_current_merchant)):
    result = complete_after_sale(after_sale_id, merchant_id=user["user_id"])
    return {"code": 0, "data": result, "message": "success"}


@router.put("/after-sales/{after_sale_id}/confirm-received")
def m_confirm_return_received(after_sale_id: int, user: dict = Depends(get_current_merchant)):
    result = confirm_return_received(after_sale_id, merchant_id=user["user_id"])
    return {"code": 0, "data": result, "message": "已确认收到退货"}


class ResendExchangeRequest(BaseModel):
    tracking_number: str
    carrier: str = "SF-Express"


@router.put("/after-sales/{after_sale_id}/resend")
def m_resend_exchange(after_sale_id: int, req: ResendExchangeRequest, user: dict = Depends(get_current_merchant)):
    """商家填写换货物流（换货流程最后一步）"""
    result = resend_exchange(after_sale_id, merchant_id=user["user_id"], tracking_number=req.tracking_number, carrier=req.carrier)
    return {"code": 0, "data": result, "message": "换货已重新发出"}
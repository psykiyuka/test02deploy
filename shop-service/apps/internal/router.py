from fastapi import APIRouter, Depends, Query

from apps.common.auth import verify_internal_token
from domain.order import get_orders, get_order_detail
from domain.logistics import get_logistics
from domain.after_sale import get_after_sales
from domain.product import get_product_list, get_product_detail
from domain.user import get_user_profile

router = APIRouter(prefix="/internal", tags=["内部接口"])


@router.get("/orders")
def internal_get_orders(
    user_id: int = Query(...),
    page: int = Query(1),
    size: int = Query(20),
    _token: bool = Depends(verify_internal_token),
):
    result = get_orders(user_id=user_id, page=page, size=size)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/orders/{order_id}")
def internal_get_order_detail(
    order_id: int,
    user_id: int = Query(...),
    _token: bool = Depends(verify_internal_token),
):
    result = get_order_detail(user_id=user_id, order_id=order_id)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/logistics")
def internal_get_logistics(
    user_id: int = Query(...),
    _token: bool = Depends(verify_internal_token),
):
    result = get_logistics(user_id=user_id)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/after-sales")
def internal_get_after_sales(
    user_id: int = Query(...),
    _token: bool = Depends(verify_internal_token),
):
    result = get_after_sales(user_id=user_id)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/products/search")
def internal_search_products(
    keyword: str = Query(...),
    page: int = Query(1),
    size: int = Query(20),
    _token: bool = Depends(verify_internal_token),
):
    result = get_product_list(keyword=keyword, page=page, size=size)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/products/{product_id}")
def internal_get_product(
    product_id: int,
    _token: bool = Depends(verify_internal_token),
):
    result = get_product_detail(product_id=product_id, check_status=False)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/users/{user_id}")
def internal_get_user(
    user_id: int,
    _token: bool = Depends(verify_internal_token),
):
    result = get_user_profile(user_id=user_id)
    return {"code": 0, "data": result, "message": "success"}

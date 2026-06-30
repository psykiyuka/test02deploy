from fastapi import APIRouter, Depends

from apps.common.auth import get_current_user
from domain.order import create_order, pay_order, cancel_order, confirm_delivery, get_orders, get_order_detail, delete_order, direct_buy
from .schema import CreateOrderRequest, DirectBuyRequest

router = APIRouter(prefix="/c-endpoint/orders", tags=["C端-订单"])


@router.post("")
def c_create_order(req: CreateOrderRequest, user: dict = Depends(get_current_user)):
    order = create_order(user["user_id"], req.address, req.product_ids)
    return {"code": 0, "data": order, "message": "success"}


@router.post("/direct-buy")
def c_direct_buy(req: DirectBuyRequest, user: dict = Depends(get_current_user)):
    """立即购买：直接下单指定商品，不走购物车"""
    order = direct_buy(user["user_id"], req.product_id, req.quantity, req.address)
    return {"code": 0, "data": order, "message": "success"}


@router.post("/{order_id}/pay")
def c_pay_order(order_id: int, user: dict = Depends(get_current_user)):
    order = pay_order(user["user_id"], order_id)
    return {"code": 0, "data": order, "message": "success"}


@router.put("/{order_id}/cancel")
def c_cancel_order(order_id: int, user: dict = Depends(get_current_user)):
    order = cancel_order(user["user_id"], order_id)
    return {"code": 0, "data": order, "message": "success"}


@router.put("/{order_id}/confirm")
def c_confirm_delivery(order_id: int, user: dict = Depends(get_current_user)):
    order = confirm_delivery(user["user_id"], order_id)
    return {"code": 0, "data": order, "message": "确认收货成功"}


@router.get("")
def c_get_orders(status: str = None, page: int = 1, size: int = 20, user: dict = Depends(get_current_user)):
    result = get_orders(user["user_id"], status=status, page=page, size=size)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/{order_id}")
def c_get_order_detail(order_id: int, user: dict = Depends(get_current_user)):
    order = get_order_detail(user["user_id"], order_id)
    return {"code": 0, "data": order, "message": "success"}


@router.delete("/{order_id}")
def c_delete_order(order_id: int, user: dict = Depends(get_current_user)):
    order = delete_order(order_id, user_id=user["user_id"])
    return {"code": 0, "data": order, "message": "订单已删除"}

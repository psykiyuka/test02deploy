from fastapi import APIRouter, Depends, Query

from apps.common.auth import get_current_admin
from domain.order import get_all_orders, delete_order

router = APIRouter(prefix="/b-endpoint/orders", tags=["B端-订单管理"])


@router.get("")
def b_get_all_orders(
    status: str = Query(None),
    page: int = Query(1),
    size: int = Query(20),
    admin: dict = Depends(get_current_admin),
):
    result = get_all_orders(status=status, page=page, size=size)
    return {"code": 0, "data": result, "message": "success"}


@router.delete("/{order_id}")
def b_delete_order(order_id: int, admin: dict = Depends(get_current_admin)):
    result = delete_order(order_id)
    return {"code": 0, "data": result, "message": "订单已删除"}

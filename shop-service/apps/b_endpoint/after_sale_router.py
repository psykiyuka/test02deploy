from fastapi import APIRouter, Depends, Query

from apps.common.auth import get_current_admin
from domain.after_sale import get_all_after_sales, delete_after_sale

router = APIRouter(prefix="/b-endpoint/after-sales", tags=["B端-售后管理"])


@router.get("")
def b_get_after_sales(
    status: str = Query(None),
    page: int = Query(1),
    size: int = Query(20),
    admin: dict = Depends(get_current_admin),
):
    result = get_all_after_sales(status=status, page=page, size=size)
    return {"code": 0, "data": result, "message": "success"}


@router.delete("/{after_sale_id}")
def b_delete_after_sale(after_sale_id: int, admin: dict = Depends(get_current_admin)):
    result = delete_after_sale(after_sale_id)
    return {"code": 0, "data": result, "message": "售后记录已删除"}

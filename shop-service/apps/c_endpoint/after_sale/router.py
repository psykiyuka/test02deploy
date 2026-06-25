from fastapi import APIRouter, Depends

from apps.common.auth import get_current_user
from domain.after_sale import create_after_sale, get_after_sale_detail, get_after_sales, cancel_after_sale, submit_return_logistics
from .schema import CreateAfterSaleRequest, SubmitReturnLogisticsRequest

router = APIRouter(prefix="/c-endpoint/after-sales", tags=["C端-售后"])


@router.post("")
def c_create_after_sale(req: CreateAfterSaleRequest, user: dict = Depends(get_current_user)):
    result = create_after_sale(user["user_id"], req.order_id, req.type, req.reason)
    return {"code": 0, "data": result, "message": "success"}


@router.get("")
def c_get_after_sales(user: dict = Depends(get_current_user)):
    records = get_after_sales(user["user_id"])
    return {"code": 0, "data": records, "message": "success"}


@router.get("/{after_sale_id}")
def c_get_after_sale_detail(after_sale_id: int, user: dict = Depends(get_current_user)):
    result = get_after_sale_detail(after_sale_id, user["user_id"])
    return {"code": 0, "data": result, "message": "success"}


@router.put("/{after_sale_id}/cancel")
def c_cancel_after_sale(after_sale_id: int, user: dict = Depends(get_current_user)):
    result = cancel_after_sale(after_sale_id, user["user_id"])
    return {"code": 0, "data": result, "message": "售后申请已取消"}


@router.put("/{after_sale_id}/return-logistics")
def c_submit_return_logistics(after_sale_id: int, req: SubmitReturnLogisticsRequest, user: dict = Depends(get_current_user)):
    result = submit_return_logistics(after_sale_id, user["user_id"], req.tracking_number, req.carrier)
    return {"code": 0, "data": result, "message": "退货物流信息已提交"}

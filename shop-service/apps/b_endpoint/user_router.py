from fastapi import APIRouter, Depends, Query

from apps.common.auth import get_current_admin
from domain.user import approve_merchant, reject_merchant, reset_password, get_all_users, get_user_profile, delete_user, get_email_change_requests, approve_email_change, reject_email_change
from apps.b_endpoint.user_schema import ResetPasswordRequest, RejectMerchantRequest

router = APIRouter(prefix="/b-endpoint/users", tags=["B端-用户管理"])


# ========== 邮箱换绑审核（必须放在 /{user_id} 路由之前，否则 email-changes 会被当作 user_id） ==========

@router.get("/email-changes")
def b_get_email_changes(
    page: int = Query(1),
    size: int = Query(20),
    status: str = Query(None),
    admin: dict = Depends(get_current_admin),
):
    result = get_email_change_requests(page=page, size=size, status=status)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/email-changes/{request_id}/approve")
def b_approve_email_change(
    request_id: int,
    admin: dict = Depends(get_current_admin),
):
    result = approve_email_change(request_id)
    return {"code": 0, "data": result, "message": "已通过邮箱换绑申请"}


@router.put("/email-changes/{request_id}/reject")
def b_reject_email_change(
    request_id: int,
    reason: str = Query(None),
    admin: dict = Depends(get_current_admin),
):
    result = reject_email_change(request_id, reason)
    return {"code": 0, "data": result, "message": "已拒绝邮箱换绑申请"}


@router.get("")
def b_get_users(
    page: int = Query(1),
    size: int = Query(20),
    role: str = Query(None),
    merchant_status: str = Query(None),
    admin: dict = Depends(get_current_admin),
):
    result = get_all_users(page, size, role, merchant_status)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/{user_id}")
def b_get_user_detail(user_id: int, admin: dict = Depends(get_current_admin)):
    user = get_user_profile(user_id)
    return {"code": 0, "data": user, "message": "success"}


@router.put("/{user_id}/password")
def b_reset_password(user_id: int, req: ResetPasswordRequest, admin: dict = Depends(get_current_admin)):
    result = reset_password(user_id, req.new_password)
    return {"code": 0, "data": result, "message": "密码重置成功"}


@router.put("/{user_id}/merchant/approve")
def b_approve_merchant(user_id: int, admin: dict = Depends(get_current_admin)):
    result = approve_merchant(user_id)
    return {"code": 0, "data": result, "message": "商家审核通过"}


@router.put("/{user_id}/merchant/reject")
def b_reject_merchant(user_id: int, req: RejectMerchantRequest = None, admin: dict = Depends(get_current_admin)):
    reason = req.reason if req else None
    result = reject_merchant(user_id, reason=reason)
    return {"code": 0, "data": result, "message": "商家审核拒绝"}


@router.delete("/{user_id}")
def b_delete_user(user_id: int, admin: dict = Depends(get_current_admin)):
    result = delete_user(user_id)
    return {"code": 0, "data": result, "message": "用户已删除"}

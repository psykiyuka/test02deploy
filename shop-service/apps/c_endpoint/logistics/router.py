from fastapi import APIRouter, Depends, Query

from apps.common.auth import get_current_user
from domain.logistics import get_logistics

router = APIRouter(prefix="/c-endpoint/logistics", tags=["C端-物流"])


@router.get("")
def c_get_logistics(
    order_id: int = Query(None),
    user: dict = Depends(get_current_user),
):
    result = get_logistics(user["user_id"], order_id=order_id)
    return {"code": 0, "data": result, "message": "success"}
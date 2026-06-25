import logging
from fastapi import APIRouter, Depends
from apps.common.auth import get_current_user

logger = logging.getLogger("shop")
router = APIRouter(prefix="/c-endpoint/favorites", dependencies=[Depends(get_current_user)])


@router.post("/{product_id}")
def add_favorite(product_id: int, user: dict = Depends(get_current_user)):
    from domain.user.favorite_service import add_favorite as svc_add
    result = svc_add(user["user_id"], product_id)
    return {"code": 0, "data": result, "message": "收藏成功"}


@router.delete("/{product_id}")
def remove_favorite(product_id: int, user: dict = Depends(get_current_user)):
    from domain.user.favorite_service import remove_favorite as svc_remove
    result = svc_remove(user["user_id"], product_id)
    return {"code": 0, "data": result, "message": "已取消收藏"}


@router.get("")
def list_favorites(page: int = 1, size: int = 20, user: dict = Depends(get_current_user)):
    from domain.user.favorite_service import get_favorites as svc_get
    result = svc_get(user["user_id"], page, size)
    return {"code": 0, "data": result}


@router.get("/check/{product_id}")
def check_favorite(product_id: int, user: dict = Depends(get_current_user)):
    from domain.user.favorite_service import check_favorite as svc_check
    result = svc_check(user["user_id"], product_id)
    return {"code": 0, "data": result}

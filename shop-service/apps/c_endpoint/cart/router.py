from fastapi import APIRouter, Depends

from apps.common.auth import get_current_user
from domain.cart import add_to_cart, update_cart_item, remove_from_cart, get_cart
from .schema import AddCartRequest, UpdateCartRequest

router = APIRouter(prefix="/c-endpoint/cart", tags=["C端-购物车"])


@router.get("")
def c_get_cart(user: dict = Depends(get_current_user)):
    items = get_cart(user["user_id"])
    return {"code": 0, "data": items, "message": "success"}


@router.post("")
def c_add_to_cart(req: AddCartRequest, user: dict = Depends(get_current_user)):
    result = add_to_cart(user["user_id"], req.product_id, req.quantity)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/{product_id}")
def c_update_cart_item(product_id: int, req: UpdateCartRequest, user: dict = Depends(get_current_user)):
    result = update_cart_item(user["user_id"], product_id, req.quantity)
    return {"code": 0, "data": result, "message": "success"}


@router.delete("/{product_id}")
def c_remove_from_cart(product_id: int, user: dict = Depends(get_current_user)):
    result = remove_from_cart(user["user_id"], product_id)
    return {"code": 0, "data": result, "message": "success"}
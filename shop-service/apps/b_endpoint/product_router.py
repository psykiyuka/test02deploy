from fastapi import APIRouter, Depends, Query

from apps.common.auth import get_current_admin
from domain.product import create_product, update_product, toggle_product_status, approve_product, reject_product, delete_product, get_all_products, get_pending_products
from apps.c_endpoint.product.schema import CreateProductRequest, UpdateProductRequest, ToggleStatusRequest

router = APIRouter(prefix="/b-endpoint/products", tags=["B端-商品管理"])


@router.get("")
def b_get_all_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    approval_status: str = Query(None),
    admin: dict = Depends(get_current_admin),
):
    result = get_all_products(page, size, approval_status)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/pending")
def b_get_pending_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_current_admin),
):
    result = get_pending_products(page, size)
    return {"code": 0, "data": result, "message": "success"}


@router.post("")
def b_create_product(req: CreateProductRequest, admin: dict = Depends(get_current_admin)):
    result = create_product(req.name, req.description, req.price, req.image_url, req.stock, req.category_id)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/{product_id}")
def b_update_product(product_id: int, req: UpdateProductRequest, admin: dict = Depends(get_current_admin)):
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


@router.put("/{product_id}/status")
def b_toggle_status(product_id: int, req: ToggleStatusRequest, admin: dict = Depends(get_current_admin)):
    result = toggle_product_status(product_id, req.status)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/{product_id}/approve")
def b_approve_product(product_id: int, admin: dict = Depends(get_current_admin)):
    result = approve_product(product_id)
    return {"code": 0, "data": result, "message": "商品审核通过"}


@router.put("/{product_id}/reject")
def b_reject_product(product_id: int, admin: dict = Depends(get_current_admin)):
    result = reject_product(product_id)
    return {"code": 0, "data": result, "message": "商品审核拒绝"}


@router.delete("/{product_id}")
def b_delete_product(product_id: int, admin: dict = Depends(get_current_admin)):
    result = delete_product(product_id)
    return {"code": 0, "data": result, "message": "商品已删除"}
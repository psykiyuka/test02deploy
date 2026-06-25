from fastapi import APIRouter, Depends

from apps.common.auth import get_current_admin
from domain.category import get_category_tree, create_category, update_category, delete_category
from .schema import CreateCategoryRequest, UpdateCategoryRequest

router = APIRouter(prefix="/b-endpoint/categories", tags=["B端-分类管理"])


@router.get("")
def b_get_categories(admin: dict = Depends(get_current_admin)):
    tree = get_category_tree()
    return {"code": 0, "data": tree, "message": "success"}


@router.post("")
def b_create_category(req: CreateCategoryRequest, admin: dict = Depends(get_current_admin)):
    result = create_category(req.name, req.parent_id)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/{category_id}")
def b_update_category(category_id: int, req: UpdateCategoryRequest, admin: dict = Depends(get_current_admin)):
    result = update_category(category_id, req.name, req.parent_id)
    return {"code": 0, "data": result, "message": "success"}


@router.delete("/{category_id}")
def b_delete_category(category_id: int, admin: dict = Depends(get_current_admin)):
    result = delete_category(category_id)
    return {"code": 0, "data": result, "message": "success"}
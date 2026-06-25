from fastapi import APIRouter

from domain.category.category_service import get_category_tree

router = APIRouter(prefix="/c-endpoint/categories", tags=["C端-分类"])


@router.get("")
def c_get_categories():
    tree = get_category_tree()
    return {"code": 0, "data": tree, "message": "success"}
from fastapi import APIRouter

from domain.product import get_hot_products, get_product_list, get_product_detail

router = APIRouter(prefix="/c-endpoint/products", tags=["C端-商品"])


@router.get("/hot")
def c_get_hot_products():
    products = get_hot_products()
    return {"code": 0, "data": products, "message": "success"}


@router.get("")
def c_get_products(
    category_id: int = None,
    keyword: str = None,
    page: int = 1,
    size: int = 20,
    sort_by: str = "default",
    min_price: float = None,
    max_price: float = None,
    in_stock: bool = None,
):
    result = get_product_list(
        category_id=category_id,
        keyword=keyword,
        page=page,
        size=size,
        sort_by=sort_by,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
    )
    return {"code": 0, "data": result, "message": "success"}


@router.get("/{product_id}")
def c_get_product_detail(product_id: int):
    product = get_product_detail(product_id, check_status=True)
    return {"code": 0, "data": product, "message": "success"}
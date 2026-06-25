import logging
import threading

from infrastructure.database import get_cursor
from infrastructure.redis_client import get_cache, set_cache, delete_keys
from common.exceptions import NotFoundError, BusinessError
from common.utils import format_date_fields

logger = logging.getLogger("shop")

_cache_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _get_cache_lock(key: str) -> threading.Lock:
    with _locks_guard:
        if key not in _cache_locks:
            _cache_locks[key] = threading.Lock()
        return _cache_locks[key]


def get_hot_products() -> list:
    cache_key = "hot:products:list"
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    lock = _get_cache_lock(cache_key)
    with lock:
        cached = get_cache(cache_key)
        if cached is not None:
            return cached

        with get_cursor() as cur:
            cur.execute(
                "SELECT p.id, p.name, p.price, p.image_url, p.stock, p.category_id, p.discount, p.sales, c.name as category_name "
                "FROM shop.products p JOIN shop.categories c ON p.category_id = c.id "
                "WHERE p.status = 'on_sale' AND p.approval_status = 'approved' ORDER BY p.created_at DESC LIMIT 5"
            )
            products = [dict(row) for row in cur.fetchall()]

        set_cache(cache_key, products, ttl=300)
        return products


def get_product_list(
    category_id: int = None,
    keyword: str = None,
    page: int = 1,
    size: int = 20,
    sort_by: str = "default",
    sort_order: str = "desc",
    min_price: float = None,
    max_price: float = None,
    in_stock: bool = None,
) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = ["p.status = 'on_sale'", "p.approval_status = 'approved'"]
    params = []

    if category_id is not None:
        conditions.append("(p.category_id = %s OR c.parent_id = %s)")
        params.extend([category_id, category_id])
    if keyword:
        conditions.append("p.name ILIKE %s")
        params.append(f"%{keyword}%")
    if min_price is not None:
        conditions.append("p.price >= %s")
        params.append(min_price)
    if max_price is not None:
        conditions.append("p.price <= %s")
        params.append(max_price)
    if in_stock:
        conditions.append("p.stock > 0")

    where = " AND ".join(conditions)

    # 排序字段映射
    sort_map = {
        "price-asc": "p.price ASC",
        "price-desc": "p.price DESC",
        "sales": "p.sales DESC",
        "newest": "p.created_at DESC",
        "default": "p.created_at DESC",
    }
    order_clause = sort_map.get(sort_by, "p.created_at DESC")
    if sort_by == "price-asc":
        order_clause = "p.price ASC"
    elif sort_by == "price-desc":
        order_clause = "p.price DESC"
    elif sort_by == "sales":
        order_clause = "COALESCE(p.sales, 0) DESC"
    else:
        order_clause = "p.created_at DESC"

    with get_cursor() as cur:
        count_sql = (
            f"SELECT COUNT(*) as total FROM shop.products p "
            f"LEFT JOIN shop.categories c ON p.category_id = c.id WHERE {where}"
        )
        cur.execute(count_sql, params)
        total = cur.fetchone()["total"]

        query_sql = (
            f"SELECT p.id, p.name, p.description, p.price, p.image_url, p.stock, "
            f"p.category_id, p.discount, p.sales, c.name as category_name "
            f"FROM shop.products p LEFT JOIN shop.categories c ON p.category_id = c.id "
            f"WHERE {where} ORDER BY {order_clause} LIMIT %s OFFSET %s"
        )
        cur.execute(query_sql, params + [size, offset])
        items = [dict(row) for row in cur.fetchall()]

    return {"items": items, "total": total, "page": page, "size": size}


def get_product_detail(product_id: int, check_status: bool = True) -> dict:
    cache_key = f"product:{product_id}"
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    lock = _get_cache_lock(cache_key)
    with lock:
        cached = get_cache(cache_key)
        if cached is not None:
            return cached

        with get_cursor() as cur:
            conditions = "WHERE p.id = %s"
            if check_status:
                conditions += " AND p.approval_status = 'approved'"
            cur.execute(
                f"SELECT p.*, c.name as category_name FROM shop.products p "
                f"LEFT JOIN shop.categories c ON p.category_id = c.id {conditions}",
                (product_id,),
            )
            row = cur.fetchone()
            if not row:
                raise NotFoundError("商品不存在")

            product = dict(row)
            format_date_fields(product, ("created_at", "updated_at"))

            set_cache(cache_key, product, ttl=600)
            return product


def create_product(name: str, description: str, price: float, image_url: str, stock: int, category_id: int, merchant_id: int = None) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT id FROM shop.categories WHERE id = %s", (category_id,))
        if not cur.fetchone():
            raise NotFoundError("分类不存在")

        if merchant_id:
            cur.execute(
                "INSERT INTO shop.products (name, description, price, image_url, stock, category_id, merchant_id, approval_status, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                (name, description, price, image_url, stock, category_id, merchant_id, "pending", "off_sale"),
            )
        else:
            cur.execute(
                "INSERT INTO shop.products (name, description, price, image_url, stock, category_id) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
                (name, description, price, image_url, stock, category_id),
            )
        result = dict(cur.fetchone())

    delete_keys("hot:products:list")
    return result


def update_product(product_id: int, **fields) -> dict:
    allowed = {"name", "description", "price", "image_url", "stock", "category_id"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}

    if not updates:
        raise BusinessError("没有需要更新的字段")

    with get_cursor() as cur:
        set_clauses = ["updated_at = NOW()"]
        params = []
        for k, v in updates.items():
            set_clauses.append(f"{k} = %s")
            params.append(v)

        params.append(product_id)
        cur.execute(
            f"UPDATE shop.products SET {', '.join(set_clauses)} WHERE id = %s RETURNING *",
            params,
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("商品不存在")
        result = dict(row)

    delete_keys(f"product:{product_id}", "hot:products:list")
    return result


def toggle_product_status(product_id: int, status: str) -> dict:
    if status not in ("on_sale", "off_sale"):
        raise BusinessError("状态值无效，应为 on_sale 或 off_sale")

    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.products SET status = %s, updated_at = NOW() WHERE id = %s RETURNING *",
            (status, product_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("商品不存在")
        result = dict(row)

    delete_keys(f"product:{product_id}", "hot:products:list")
    return result


def approve_product(product_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.products SET approval_status = 'approved', status = 'on_sale', updated_at = NOW() WHERE id = %s RETURNING *",
            (product_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("商品不存在")
        result = dict(row)

    delete_keys(f"product:{product_id}", "hot:products:list")
    return result


def reject_product(product_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.products SET approval_status = 'rejected', status = 'off_sale', updated_at = NOW() WHERE id = %s RETURNING *",
            (product_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("商品不存在")
        result = dict(row)

    delete_keys(f"product:{product_id}", "hot:products:list")
    return result


def delete_product(product_id: int) -> dict:
    """删除商品，同时清理关联的购物车记录和缓存"""
    with get_cursor() as cur:
        # 先查商品是否存在
        cur.execute("SELECT * FROM shop.products WHERE id = %s", (product_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("商品不存在")
        product = dict(row)

        # 清理购物车中引用该商品的记录
        cur.execute("DELETE FROM shop.cart_items WHERE product_id = %s", (product_id,))

        # 删除商品
        cur.execute("DELETE FROM shop.products WHERE id = %s", (product_id,))

    delete_keys(f"product:{product_id}", "hot:products:list")
    logger.info("商品已删除 | product_id=%s name=%s", product_id, product.get("name"))
    return product


def get_products_by_merchant(merchant_id: int, page: int = 1, size: int = 20) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size

    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) as total FROM shop.products WHERE merchant_id = %s",
            (merchant_id,),
        )
        total = cur.fetchone()["total"]

        cur.execute(
            "SELECT p.id, p.name, p.price, p.image_url, p.stock, p.category_id, p.status, p.approval_status, c.name as category_name, p.created_at "
            "FROM shop.products p LEFT JOIN shop.categories c ON p.category_id = c.id "
            "WHERE p.merchant_id = %s ORDER BY p.created_at DESC LIMIT %s OFFSET %s",
            (merchant_id, size, offset),
        )
        items = [dict(row) for row in cur.fetchall()]

    return {"items": items, "total": total, "page": page, "size": size}


def get_pending_products(page: int = 1, size: int = 20) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size

    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) as total FROM shop.products WHERE approval_status = 'pending'",
        )
        total = cur.fetchone()["total"]

        cur.execute(
            "SELECT p.id, p.name, p.price, p.image_url, p.stock, p.category_id, p.merchant_id, p.approval_status, c.name as category_name, u.shop_name, p.created_at "
            "FROM shop.products p "
            "LEFT JOIN shop.categories c ON p.category_id = c.id "
            "LEFT JOIN shop.users u ON p.merchant_id = u.id "
            "WHERE p.approval_status = 'pending' ORDER BY p.created_at DESC LIMIT %s OFFSET %s",
            (size, offset),
        )
        items = [dict(row) for row in cur.fetchall()]

    return {"items": items, "total": total, "page": page, "size": size}


def get_all_products(page: int = 1, size: int = 20, approval_status: str = None) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = []
    params = []
    
    if approval_status:
        conditions.append("p.approval_status = %s")
        params.append(approval_status)
    
    where = " AND ".join(conditions) if conditions else "1=1"

    with get_cursor() as cur:
        cur.execute(
            f"SELECT COUNT(*) as total FROM shop.products p WHERE {where}",
            params,
        )
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT p.id, p.name, p.price, p.image_url, p.stock, p.category_id, p.merchant_id, p.status, p.approval_status, c.name as category_name, u.shop_name, p.created_at "
            f"FROM shop.products p "
            f"LEFT JOIN shop.categories c ON p.category_id = c.id "
            f"LEFT JOIN shop.users u ON p.merchant_id = u.id "
            f"WHERE {where} ORDER BY p.created_at DESC LIMIT %s OFFSET %s",
            params + [size, offset],
        )
        items = [dict(row) for row in cur.fetchall()]

    return {"items": items, "total": total, "page": page, "size": size}
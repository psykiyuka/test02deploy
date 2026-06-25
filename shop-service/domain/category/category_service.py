import logging

from infrastructure.database import get_cursor
from infrastructure.redis_client import delete_cache, get_cache, set_cache
from common.exceptions import NotFoundError, BusinessError

logger = logging.getLogger("shop")


def get_category_tree() -> list:
    cache_key = "categories:tree"
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    with get_cursor() as cur:
        cur.execute("SELECT id, name, parent_id, sort_order FROM shop.categories ORDER BY sort_order")
        result = [dict(row) for row in cur.fetchall()]

    set_cache(cache_key, result, ttl=600)
    return result


def create_category(name: str, parent_id: int = None) -> dict:
    with get_cursor() as cur:
        if parent_id is not None:
            cur.execute("SELECT id FROM shop.categories WHERE id = %s", (parent_id,))
            if not cur.fetchone():
                raise NotFoundError("父级分类不存在")

        cur.execute(
            "INSERT INTO shop.categories (name, parent_id) VALUES (%s, %s) RETURNING id, name, parent_id, sort_order",
            (name, parent_id),
        )
        result = dict(cur.fetchone())

    delete_cache("categories:tree")
    return result


def update_category(category_id: int, name: str = None, parent_id: int = None) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT id FROM shop.categories WHERE id = %s", (category_id,))
        if not cur.fetchone():
            raise NotFoundError("分类不存在")

        set_clauses = []
        params = []
        if name is not None:
            set_clauses.append("name = %s")
            params.append(name)
        if parent_id is not None:
            set_clauses.append("parent_id = %s")
            params.append(parent_id)

        if not set_clauses:
            raise BusinessError("没有需要更新的字段")

        params.append(category_id)
        cur.execute(
            f"UPDATE shop.categories SET {', '.join(set_clauses)} WHERE id = %s RETURNING id, name, parent_id, sort_order",
            params,
        )
        result = dict(cur.fetchone())

    delete_cache("categories:tree")
    return result


def delete_category(category_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT id FROM shop.categories WHERE id = %s", (category_id,))
        if not cur.fetchone():
            raise NotFoundError("分类不存在")

        cur.execute("SELECT COUNT(*) as cnt FROM shop.products WHERE category_id = %s", (category_id,))
        if cur.fetchone()["cnt"] > 0:
            raise BusinessError("该分类下有商品，无法删除")

        cur.execute("SELECT COUNT(*) as cnt FROM shop.categories WHERE parent_id = %s", (category_id,))
        if cur.fetchone()["cnt"] > 0:
            raise BusinessError("该分类下有子分类，无法删除")

        cur.execute("DELETE FROM shop.categories WHERE id = %s", (category_id,))

    delete_cache("categories:tree")
    return {"id": category_id, "deleted": True}
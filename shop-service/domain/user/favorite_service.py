import logging

from infrastructure.database import get_cursor
from common.exceptions import NotFoundError, BusinessError

logger = logging.getLogger("shop")


def add_favorite(user_id: int, product_id: int) -> dict:
    """添加收藏"""
    with get_cursor() as cur:
        # 验证商品存在且在售
        cur.execute(
            "SELECT id, name FROM shop.products WHERE id = %s AND status = 'on_sale'",
            (product_id,),
        )
        product = cur.fetchone()
        if not product:
            raise NotFoundError("商品不存在或未上架")

        # 插入收藏（忽略已存在的唯一约束冲突）
        cur.execute(
            "INSERT INTO shop.user_favorites (user_id, product_id) VALUES (%s, %s) "
            "ON CONFLICT (user_id, product_id) DO NOTHING RETURNING id",
            (user_id, product_id),
        )
        row = cur.fetchone()
        if row:
            logger.info("添加收藏 | user_id=%s product_id=%s", user_id, product_id)
            return {"product_id": product_id, "name": product["name"]}

        # 已收藏
        return {"product_id": product_id, "name": product["name"]}


def remove_favorite(user_id: int, product_id: int) -> dict:
    """取消收藏"""
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM shop.user_favorites WHERE user_id = %s AND product_id = %s RETURNING id",
            (user_id, product_id),
        )
        if not cur.fetchone():
            raise NotFoundError("未收藏该商品")
        logger.info("取消收藏 | user_id=%s product_id=%s", user_id, product_id)
        return {"product_id": product_id}


def get_favorites(user_id: int, page: int = 1, size: int = 20) -> dict:
    """获取收藏列表"""
    size = min(max(size, 1), 100)
    offset = (page - 1) * size

    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) as total FROM shop.user_favorites WHERE user_id = %s",
            (user_id,),
        )
        total = cur.fetchone()["total"]

        cur.execute(
            "SELECT f.id as favorite_id, f.created_at as favorited_at, "
            "p.id, p.name, p.price, p.image_url, p.stock, p.category_id, c.name as category_name "
            "FROM shop.user_favorites f "
            "JOIN shop.products p ON f.product_id = p.id "
            "LEFT JOIN shop.categories c ON p.category_id = c.id "
            "WHERE f.user_id = %s AND p.status = 'on_sale' "
            "ORDER BY f.created_at DESC LIMIT %s OFFSET %s",
            (user_id, size, offset),
        )
        items = [dict(row) for row in cur.fetchall()]

    return {"items": items, "total": total, "page": page, "size": size}


def check_favorite(user_id: int, product_id: int) -> dict:
    """检查商品是否已收藏"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT 1 FROM shop.user_favorites WHERE user_id = %s AND product_id = %s",
            (user_id, product_id),
        )
        return {"is_favorited": cur.fetchone() is not None}

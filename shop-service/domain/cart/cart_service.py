import logging

from infrastructure.database import get_cursor
from common.exceptions import NotFoundError, BusinessError

logger = logging.getLogger("shop")


def add_to_cart(user_id: int, product_id: int, quantity: int) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT id, status, stock FROM shop.products WHERE id = %s", (product_id,))
        product = cur.fetchone()
        if not product:
            raise NotFoundError("商品不存在")
        if product["status"] != "on_sale":
            raise BusinessError("商品已下架，无法添加")

        cur.execute(
            "INSERT INTO shop.cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s) "
            "ON CONFLICT (user_id, product_id) DO UPDATE SET quantity = shop.cart_items.quantity + EXCLUDED.quantity "
            "RETURNING id, user_id, product_id, quantity",
            (user_id, product_id, quantity),
        )
        return dict(cur.fetchone())


def update_cart_item(user_id: int, product_id: int, quantity: int) -> dict:
    if quantity <= 0:
        raise BusinessError("数量必须大于0")

    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.cart_items SET quantity = %s WHERE user_id = %s AND product_id = %s "
            "RETURNING id, user_id, product_id, quantity",
            (quantity, user_id, product_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("购物车中没有该商品")
        return dict(row)


def remove_from_cart(user_id: int, product_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM shop.cart_items WHERE user_id = %s AND product_id = %s",
            (user_id, product_id),
        )
    return {"product_id": product_id, "deleted": True}


def get_cart(user_id: int) -> list:
    with get_cursor() as cur:
        cur.execute(
            "SELECT ci.id, ci.product_id, ci.quantity, p.name as product_name, p.price, p.stock, p.image_url, p.status, "
            "p.merchant_id, u.shop_name "
            "FROM shop.cart_items ci JOIN shop.products p ON ci.product_id = p.id "
            "LEFT JOIN shop.users u ON p.merchant_id = u.id "
            "WHERE ci.user_id = %s ORDER BY ci.created_at DESC",
            (user_id,),
        )
        return [dict(row) for row in cur.fetchall()]
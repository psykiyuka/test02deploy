import logging
import json
from datetime import datetime, timedelta

from psycopg2.extras import RealDictCursor

from infrastructure.database import get_connection, release_connection, get_cursor
from infrastructure.redis_client import delete_keys
from common.exceptions import NotFoundError, BusinessError
from common.utils import format_date_fields
from domain.logistics import generate_logistics

logger = logging.getLogger("shop")


def create_order(user_id: int, address: str) -> dict:
    if not address or not address.strip():
        raise BusinessError("收货地址不能为空")
    if len(address.strip()) < 5:
        raise BusinessError("收货地址过短，请填写完整地址")

    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT ci.product_id, ci.quantity, p.name, p.price, p.stock, p.merchant_id "
                "FROM shop.cart_items ci JOIN shop.products p ON ci.product_id = p.id "
                "WHERE ci.user_id = %s FOR UPDATE OF p",
                (user_id,),
            )
            cart_items = [dict(row) for row in cur.fetchall()]
            if not cart_items:
                raise BusinessError("购物车为空，无法下单")

            for item in cart_items:
                if item["stock"] < item["quantity"]:
                    raise BusinessError(f"商品 [{item['name']}] 库存不足")

            # 按 merchant_id 分组，每个商家一个独立订单
            groups: dict[int, list] = {}
            for item in cart_items:
                mid = item.get("merchant_id") or 0
                groups.setdefault(mid, []).append(item)

            created_orders = []
            all_product_ids = set()

            for merchant_id, items in groups.items():
                total_amount = sum(item["price"] * item["quantity"] for item in items)

                for item in items:
                    cur.execute(
                        "UPDATE shop.products SET stock = stock - %s WHERE id = %s AND stock >= %s",
                        (item["quantity"], item["product_id"], item["quantity"]),
                    )

                cur.execute(
                    "INSERT INTO shop.orders (user_id, total_amount, address, merchant_id) VALUES (%s, %s, %s, %s) RETURNING id",
                    (user_id, total_amount, address, merchant_id if merchant_id else None),
                )
                order_id = cur.fetchone()["id"]

                for item in items:
                    cur.execute(
                        "INSERT INTO shop.order_items (order_id, product_id, product_name, price, quantity) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (order_id, item["product_id"], item["name"], item["price"], item["quantity"]),
                    )
                    all_product_ids.add(item["product_id"])

                cur.execute("SELECT * FROM shop.orders WHERE id = %s", (order_id,))
                order = dict(cur.fetchone())
                format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))
                created_orders.append(order)

                logger.info("订单创建成功 | order_id=%s | user_id=%s | merchant_id=%s | amount=%.2f",
                            order_id, user_id, merchant_id, total_amount)

            cur.execute("DELETE FROM shop.cart_items WHERE user_id = %s", (user_id,))

        conn.commit()

        # 清除被购买商品的缓存（库存已变更）
        cache_keys = [f"product:{pid}" for pid in all_product_ids]
        cache_keys.append("hot:products:list")
        delete_keys(*cache_keys)

        return {"orders": created_orders, "count": len(created_orders)}

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True
        release_connection(conn)


def pay_order(user_id: int, order_id: int) -> dict:
    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM shop.orders WHERE id = %s FOR UPDATE",
                (order_id,),
            )
            order = cur.fetchone()
            if not order:
                raise NotFoundError("订单不存在")
            order = dict(order)

            if order["user_id"] != user_id:
                raise NotFoundError("订单不存在")

            if order["status"] == "paid":
                raise BusinessError("请勿重复支付")
            if order["status"] == "cancelled":
                raise BusinessError("订单已取消")

            cur.execute(
                "UPDATE shop.orders SET status = 'paid', paid_at = NOW() WHERE id = %s",
                (order_id,),
            )

            cur.execute(
                "INSERT INTO shop.payment_records (order_id, amount, method) VALUES (%s, %s, 'mock')",
                (order_id, order["total_amount"]),
            )

            cur.execute("SELECT * FROM shop.orders WHERE id = %s", (order_id,))
            order = dict(cur.fetchone())

        conn.commit()
        logger.info("订单支付成功 | order_id=%s", order_id)

        try:
            generate_logistics(order_id)
        except Exception:
            logger.warning("物流记录生成失败 | order_id=%s", order_id, exc_info=True)

        format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))

        return order

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True
        release_connection(conn)


def cancel_order(user_id: int, order_id: int) -> dict:
    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM shop.orders WHERE id = %s FOR UPDATE",
                (order_id,),
            )
            order = cur.fetchone()
            if not order:
                raise NotFoundError("订单不存在")
            order = dict(order)

            if order["user_id"] != user_id:
                raise NotFoundError("订单不存在")

            if order["status"] == "paid":
                raise BusinessError("订单已支付，不可取消")
            if order["status"] == "cancelled":
                raise BusinessError("订单已取消")

            cur.execute(
                "UPDATE shop.orders SET status = 'cancelled', cancelled_at = NOW() WHERE id = %s",
                (order_id,),
            )

            cur.execute(
                "SELECT product_id FROM shop.order_items WHERE order_id = %s",
                (order_id,),
            )
            cancel_product_ids = [row["product_id"] for row in cur.fetchall()]

            cur.execute(
                "UPDATE shop.products p SET stock = stock + oi.quantity "
                "FROM shop.order_items oi WHERE oi.order_id = %s AND oi.product_id = p.id",
                (order_id,),
            )

            cur.execute("SELECT * FROM shop.orders WHERE id = %s", (order_id,))
            order = dict(cur.fetchone())

        conn.commit()
        logger.info("订单已取消 | order_id=%s", order_id)

        # 清除回加库存商品的缓存
        cancel_cache_keys = [f"product:{pid}" for pid in set(cancel_product_ids)]
        cancel_cache_keys.append("hot:products:list")
        delete_keys(*cancel_cache_keys)

        format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))

        return order

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True
        release_connection(conn)


def get_orders(user_id: int, status: str = None, page: int = 1, size: int = 20) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = ["user_id = %s"]
    params = [user_id]

    if status:
        conditions.append("status = %s")
        params.append(status)

    where = " AND ".join(conditions)

    with get_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) as total FROM shop.orders WHERE {where}", params)
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT * FROM shop.orders WHERE {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params + [size, offset],
        )
        orders = [dict(row) for row in cur.fetchall()]

        if orders:
            order_ids = tuple(o["id"] for o in orders)
            cur.execute(
                f"SELECT * FROM shop.order_items WHERE order_id IN %s ORDER BY order_id, id",
                (order_ids,),
            )
            items_by_order: dict[int, list] = {}
            for row in cur.fetchall():
                item = dict(row)
                items_by_order.setdefault(item["order_id"], []).append(item)

            for order in orders:
                format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))
                order["items"] = items_by_order.get(order["id"], [])

    return {"items": orders, "total": total, "page": page, "size": size}


def get_order_detail(user_id: int, order_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.orders WHERE id = %s AND user_id = %s",
            (order_id, user_id),
        )
        order = cur.fetchone()
        if not order:
            raise NotFoundError("订单不存在")
        order = dict(order)

        cur.execute(
            "SELECT * FROM shop.order_items WHERE order_id = %s",
            (order_id,),
        )
        order["items"] = [dict(row) for row in cur.fetchall()]

        format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))

        return order


def get_all_orders(status: str = None, page: int = 1, size: int = 20) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = []
    params = []

    if status:
        conditions.append("status = %s")
        params.append(status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) as total FROM shop.orders {where}", params)
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT * FROM shop.orders {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params + [size, offset],
        )
        orders = [dict(row) for row in cur.fetchall()]

        if orders:
            order_ids = tuple(o["id"] for o in orders)
            cur.execute(
                "SELECT * FROM shop.order_items WHERE order_id IN %s ORDER BY order_id, id",
                (order_ids,),
            )
            items_by_order: dict[int, list] = {}
            for row in cur.fetchall():
                item = dict(row)
                items_by_order.setdefault(item["order_id"], []).append(item)

            for order in orders:
                format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))
                order["items"] = items_by_order.get(order["id"], [])

    return {"items": orders, "total": total, "page": page, "size": size}


def delete_order(order_id: int, user_id: int = None) -> dict:
    """删除订单（仅允许删除已取消或已完成的订单）"""
    with get_cursor() as cur:
        if user_id:
            cur.execute("SELECT * FROM shop.orders WHERE id = %s AND user_id = %s", (order_id, user_id))
        else:
            cur.execute("SELECT * FROM shop.orders WHERE id = %s", (order_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("订单不存在")
        order = dict(row)

        if order["status"] not in ("cancelled", "delivered", "completed"):
            raise BusinessError("只能删除已取消或已完成的订单")

        # 级联清理
        cur.execute("DELETE FROM shop.logistics_records WHERE order_id = %s", (order_id,))
        cur.execute("DELETE FROM shop.order_items WHERE order_id = %s", (order_id,))
        cur.execute("DELETE FROM shop.payment_records WHERE order_id = %s", (order_id,))
        cur.execute("DELETE FROM shop.orders WHERE id = %s", (order_id,))

    logger.info("订单已删除 | order_id=%s", order_id)
    return order


def cancel_timeout_orders():
    logger.info("[Scheduler] 开始扫描超时订单")
    timeout_threshold = datetime.utcnow() - timedelta(minutes=30)

    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM shop.orders WHERE status = 'pending' AND created_at < %s FOR UPDATE",
                (timeout_threshold,),
            )
            timeout_ids = [row["id"] for row in cur.fetchall()]

            if not timeout_ids:
                conn.commit()
                logger.info("[Scheduler] 无超时订单")
                return

            cur.execute(
                "UPDATE shop.orders SET status = 'cancelled', cancelled_at = NOW() "
                "WHERE id = ANY(%s)",
                (timeout_ids,),
            )

            cur.execute(
                "SELECT DISTINCT product_id FROM shop.order_items WHERE order_id = ANY(%s)",
                (timeout_ids,),
            )
            timeout_product_ids = [row["product_id"] for row in cur.fetchall()]

            cur.execute(
                "UPDATE shop.products p SET stock = stock + oi.quantity "
                "FROM shop.order_items oi WHERE oi.order_id = ANY(%s) AND oi.product_id = p.id",
                (timeout_ids,),
            )

        conn.commit()
        logger.info("[Scheduler] 扫描完成 | 取消超时订单=%d | ids=%s", len(timeout_ids), timeout_ids)

        # 清除回加库存商品的缓存
        if timeout_product_ids:
            timeout_cache_keys = [f"product:{pid}" for pid in timeout_product_ids]
            timeout_cache_keys.append("hot:products:list")
            delete_keys(*timeout_cache_keys)

    except Exception:
        conn.rollback()
        logger.error("[Scheduler] 批量取消超时订单失败", exc_info=True)
    finally:
        conn.autocommit = True
        release_connection(conn)


def get_orders_by_merchant(merchant_id: int, page: int = 1, size: int = 20) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size

    with get_cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) as total FROM shop.orders WHERE merchant_id = %s",
            (merchant_id,),
        )
        total = cur.fetchone()["total"]

        cur.execute(
            "SELECT o.*, u.email AS buyer_email, u.nickname AS buyer_nickname, "
            "lr.status AS logistics_status, lr.tracking_number AS tracking_number "
            "FROM shop.orders o "
            "LEFT JOIN shop.users u ON o.user_id = u.id "
            "LEFT JOIN shop.logistics_records lr ON o.id = lr.order_id "
            "WHERE o.merchant_id = %s ORDER BY o.created_at DESC LIMIT %s OFFSET %s",
            (merchant_id, size, offset),
        )
        orders = [dict(row) for row in cur.fetchall()]

        if orders:
            order_ids = tuple(o["id"] for o in orders)
            cur.execute(
                "SELECT oi.*, p.name as product_name, p.image_url FROM shop.order_items oi "
                "JOIN shop.products p ON oi.product_id = p.id "
                "WHERE oi.order_id IN %s ORDER BY oi.order_id, oi.id",
                (order_ids,),
            )
            items_by_order: dict[int, list] = {}
            for row in cur.fetchall():
                item = dict(row)
                items_by_order.setdefault(item["order_id"], []).append(item)

            for order in orders:
                format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))
                order["items"] = items_by_order.get(order["id"], [])

    return {"items": orders, "total": total, "page": page, "size": size}


def update_logistics_status(order_id: int, status: str, tracking_number: str = None, merchant_id: int = None) -> dict:
    # 正向物流状态（不含 returned，returned 仅售后退货场景使用）
    valid_statuses = ["pending", "picked_up", "in_transit", "out_for_delivery", "delivered"]
    if status not in valid_statuses:
        raise BusinessError(f"无效的物流状态，应为 {', '.join(valid_statuses)} 之一")

    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 校验订单归属
            if merchant_id:
                cur.execute(
                    "SELECT * FROM shop.orders WHERE id = %s AND merchant_id = %s",
                    (order_id, merchant_id),
                )
            else:
                cur.execute("SELECT * FROM shop.orders WHERE id = %s", (order_id,))

            order = cur.fetchone()
            if not order:
                raise NotFoundError("订单不存在")
            order = dict(order)

            # 同步更新订单状态
            if status in ("pending", "picked_up", "in_transit", "out_for_delivery") and order["status"] == "paid":
                cur.execute("UPDATE shop.orders SET status = 'shipped' WHERE id = %s", (order_id,))
            elif status == "delivered" and order["status"] in ("shipped", "in_transit", "out_for_delivery"):
                cur.execute("UPDATE shop.orders SET status = 'delivered' WHERE id = %s", (order_id,))

            # 读取现有物流记录
            cur.execute("SELECT * FROM shop.logistics_records WHERE order_id = %s", (order_id,))
            existing = cur.fetchone()

            new_timeline = []
            if existing:
                existing = dict(existing)
                if isinstance(existing.get("timeline"), str):
                    new_timeline = json.loads(existing["timeline"])
                elif isinstance(existing.get("timeline"), list):
                    new_timeline = existing["timeline"]

            # 追加新节点
            location_map = {
                "pending": "仓库准备中",
                "picked_up": "已从仓库发出",
                "in_transit": "运输中",
                "out_for_delivery": "派送中",
                "delivered": "已送达",
            }
            new_timeline.append({
                "time": datetime.utcnow().isoformat(),
                "status": status,
                "location": location_map.get(status, "未知"),
            })

            if existing:
                cur.execute(
                    "UPDATE shop.logistics_records SET status = %s, tracking_number = COALESCE(%s, tracking_number), "
                    "timeline = %s, current_location = %s, updated_at = NOW() WHERE order_id = %s",
                    (status, tracking_number, json.dumps(new_timeline, ensure_ascii=False),
                     location_map.get(status, ""), order_id),
                )
            else:
                cur.execute(
                    "INSERT INTO shop.logistics_records (order_id, tracking_number, carrier, status, current_location, timeline) "
                    "VALUES (%s, %s, 'SF-Express', %s, %s, %s)",
                    (order_id, tracking_number or f"SF{order_id:08d}", status,
                     location_map.get(status, ""), json.dumps(new_timeline, ensure_ascii=False)),
                )

            cur.execute("SELECT * FROM shop.logistics_records WHERE order_id = %s", (order_id,))
            result = dict(cur.fetchone())
            format_date_fields(result, ("created_at", "updated_at", "estimated_delivery"))
            if isinstance(result.get("timeline"), str):
                result["timeline"] = json.loads(result["timeline"])

        conn.commit()
        logger.info("物流状态已更新 | order_id=%s | status=%s", order_id, status)
        return result

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True
        release_connection(conn)


def confirm_delivery(user_id: int, order_id: int) -> dict:
    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM shop.orders WHERE id = %s FOR UPDATE", (order_id,))
            order = cur.fetchone()
            if not order:
                raise NotFoundError("订单不存在")
            order = dict(order)

            if order["user_id"] != user_id:
                raise NotFoundError("订单不存在")

            if order["status"] != "shipped":
                raise BusinessError("只能确认已发货的订单")

            cur.execute("UPDATE shop.orders SET status = 'delivered' WHERE id = %s", (order_id,))

            # 同步更新物流记录状态
            cur.execute("SELECT * FROM shop.logistics_records WHERE order_id = %s", (order_id,))
            logistics = cur.fetchone()
            if logistics:
                logistics = dict(logistics)
                new_timeline = []
                if isinstance(logistics.get("timeline"), str):
                    new_timeline = json.loads(logistics["timeline"])
                elif isinstance(logistics.get("timeline"), list):
                    new_timeline = logistics["timeline"]

                new_timeline.append({
                    "time": datetime.utcnow().isoformat(),
                    "status": "delivered",
                    "location": "已送达",
                })
                cur.execute(
                    "UPDATE shop.logistics_records SET status = 'delivered', current_location = '已送达', "
                    "timeline = %s, updated_at = NOW() WHERE order_id = %s",
                    (json.dumps(new_timeline, ensure_ascii=False), order_id),
                )

            cur.execute("SELECT * FROM shop.orders WHERE id = %s", (order_id,))
            order = dict(cur.fetchone())

        conn.commit()
        logger.info("用户确认收货 | order_id=%s | user_id=%s", order_id, user_id)

        format_date_fields(order, ("created_at", "paid_at", "cancelled_at"))
        return order

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True
        release_connection(conn)
import logging

from infrastructure.database import get_cursor
from common.exceptions import NotFoundError, BusinessError, PermissionDeniedError
from common.utils import format_date_fields

logger = logging.getLogger("shop")


def create_after_sale(user_id: int, order_id: int, type_: str, reason: str) -> dict:
    if type_ not in ("refund", "return", "exchange"):
        raise BusinessError("售后类型无效，应为 refund/return/exchange")

    with get_cursor() as cur:
        cur.execute(
            "SELECT id, status, merchant_id FROM shop.orders WHERE id = %s AND user_id = %s",
            (order_id, user_id),
        )
        order = cur.fetchone()
        if not order:
            raise NotFoundError("订单不存在")

        if order["status"] not in ("paid", "shipped", "delivered"):
            raise BusinessError("仅已支付/已发货/已完成的订单可申请售后")

        # 检查同一订单是否已存在进行中的售后（防止重复申请）
        cur.execute(
            "SELECT id, status FROM shop.after_sale_requests "
            "WHERE order_id = %s AND status NOT IN ('completed', 'rejected', 'cancelled') "
            "LIMIT 1",
            (order_id,),
        )
        existing = cur.fetchone()
        if existing:
            raise BusinessError(f"该订单已存在进行中的售后申请（ID: {existing['id']}），请等待处理完成后再申请")

        # 从订单的 order_items 关联 products 获取 merchant_id
        cur.execute(
            "SELECT p.merchant_id FROM shop.order_items oi "
            "JOIN shop.products p ON oi.product_id = p.id "
            "WHERE oi.order_id = %s LIMIT 1",
            (order_id,),
        )
        merchant_row = cur.fetchone()
        merchant_id = merchant_row["merchant_id"] if merchant_row else None

        cur.execute(
            "INSERT INTO shop.after_sale_requests (user_id, order_id, type, reason, merchant_id) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING *",
            (user_id, order_id, type_, reason, merchant_id),
        )
        result = dict(cur.fetchone())

        format_date_fields(result, ("created_at", "updated_at"))

        return result


def get_after_sale_detail(after_sale_id: int, user_id: int) -> dict:
    """用户获取自己的售后申请详情"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s AND user_id = %s",
            (after_sale_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        result = dict(row)
        format_date_fields(result, ("created_at", "updated_at"))
        return result


def get_after_sales(user_id: int) -> list:
    """用户获取自己的售后申请列表，关联卖家信息"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT a.*, seller.nickname as seller_name, seller.shop_name as seller_shop_name "
            "FROM shop.after_sale_requests a "
            "LEFT JOIN shop.users seller ON a.merchant_id = seller.id "
            "WHERE a.user_id = %s ORDER BY a.created_at DESC",
            (user_id,),
        )
        records = []
        for row in cur.fetchall():
            record = dict(row)
            format_date_fields(record, ("created_at", "updated_at"))
            records.append(record)
        return records


def get_after_sales_by_merchant(merchant_id: int, status: str = None, page: int = 1, size: int = 20) -> dict:
    """商家获取自己的售后申请列表，关联买家信息"""
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = ["a.merchant_id = %s"]
    params = [merchant_id]

    if status:
        conditions.append("a.status = %s")
        params.append(status)

    where = f"WHERE {' AND '.join(conditions)}"

    with get_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) as total FROM shop.after_sale_requests a {where}", params)
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT a.*, buyer.nickname as buyer_name, buyer.email as buyer_email "
            f"FROM shop.after_sale_requests a "
            f"LEFT JOIN shop.users buyer ON a.user_id = buyer.id "
            f"{where} ORDER BY a.created_at DESC LIMIT %s OFFSET %s",
            params + [size, offset],
        )
        items = []
        for row in cur.fetchall():
            record = dict(row)
            format_date_fields(record, ("created_at", "updated_at"))
            items.append(record)

    return {"items": items, "total": total, "page": page, "size": size}


def get_all_after_sales(status: str = None, page: int = 1, size: int = 20) -> dict:
    """管理员获取所有售后记录，关联买家和卖家信息"""
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = []
    params = []

    if status:
        conditions.append("a.status = %s")
        params.append(status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) as total FROM shop.after_sale_requests a {where}", params)
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT a.*, "
            f"buyer.nickname as buyer_name, buyer.email as buyer_email, "
            f"seller.nickname as seller_name, seller.shop_name as seller_shop_name "
            f"FROM shop.after_sale_requests a "
            f"LEFT JOIN shop.users buyer ON a.user_id = buyer.id "
            f"LEFT JOIN shop.users seller ON a.merchant_id = seller.id "
            f"{where} ORDER BY a.created_at DESC LIMIT %s OFFSET %s",
            params + [size, offset],
        )
        items = []
        for row in cur.fetchall():
            record = dict(row)
            format_date_fields(record, ("created_at", "updated_at"))
            items.append(record)

    return {"items": items, "total": total, "page": page, "size": size}


def _update_after_sale_status(after_sale_id: int, new_status: str, allowed_from: list[str]) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s FOR UPDATE",
            (after_sale_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        request = dict(row)

        if request["status"] not in allowed_from:
            raise BusinessError(f"当前状态 [{request['status']}] 不允许此操作")

        cur.execute(
            "UPDATE shop.after_sale_requests SET status = %s, updated_at = NOW() "
            "WHERE id = %s RETURNING *",
            (new_status, after_sale_id),
        )
        result = dict(cur.fetchone())
        format_date_fields(result, ("created_at", "updated_at"))
        return result


def _check_merchant_owner(after_sale_id: int, merchant_id: int) -> None:
    """验证售后记录是否属于指定商家"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT merchant_id FROM shop.after_sale_requests WHERE id = %s",
            (after_sale_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        if row["merchant_id"] != merchant_id:
            raise PermissionDeniedError("无权操作此售后申请")


def approve_after_sale(after_sale_id: int, merchant_id: int = None) -> dict:
    if merchant_id is not None:
        _check_merchant_owner(after_sale_id, merchant_id)

    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s FOR UPDATE",
            (after_sale_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        request = dict(row)

        if request["status"] != "pending":
            raise BusinessError(f"当前状态 [{request['status']}] 不允许此操作")

        if request["type"] == "refund":
            # 仅退款：直接完成
            cur.execute(
                "UPDATE shop.after_sale_requests "
                "SET status = 'completed', approved_at = NOW(), completed_at = NOW(), updated_at = NOW() "
                "WHERE id = %s RETURNING *",
                (after_sale_id,),
            )
        else:
            # 退货退款/换货：进入等待退货状态
            cur.execute(
                "UPDATE shop.after_sale_requests "
                "SET status = 'approved', return_status = 'pending_return', approved_at = NOW(), updated_at = NOW() "
                "WHERE id = %s RETURNING *",
                (after_sale_id,),
            )

        result = dict(cur.fetchone())
        format_date_fields(result, ("created_at", "updated_at", "approved_at", "completed_at"))
        return result


def reject_after_sale(after_sale_id: int, merchant_id: int = None) -> dict:
    if merchant_id is not None:
        _check_merchant_owner(after_sale_id, merchant_id)
    return _update_after_sale_status(after_sale_id, "rejected", ["pending"])


def complete_after_sale(after_sale_id: int, merchant_id: int = None) -> dict:
    """仅用于 refund 类型的直接完成（兼容旧逻辑）"""
    if merchant_id is not None:
        _check_merchant_owner(after_sale_id, merchant_id)
    return _update_after_sale_status(after_sale_id, "completed", ["approved"])


def submit_return_logistics(after_sale_id: int, user_id: int, tracking_number: str, carrier: str = "SF-Express") -> dict:
    """用户提交退货物流信息"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s AND user_id = %s FOR UPDATE",
            (after_sale_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        request = dict(row)

        if request["status"] != "approved" or request["return_status"] != "pending_return":
            raise BusinessError("当前状态不允许提交退货物流信息")

        cur.execute(
            "UPDATE shop.after_sale_requests "
            "SET status = 'returned', return_status = 'returned', "
            "return_tracking_number = %s, return_carrier = %s, "
            "returned_at = NOW(), updated_at = NOW() "
            "WHERE id = %s RETURNING *",
            (tracking_number, carrier, after_sale_id),
        )
        result = dict(cur.fetchone())
        format_date_fields(result, ("created_at", "updated_at", "returned_at"))
        return result


def confirm_return_received(after_sale_id: int, merchant_id: int) -> dict:
    """商家确认收到退货"""
    _check_merchant_owner(after_sale_id, merchant_id)

    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s FOR UPDATE",
            (after_sale_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        request = dict(row)

        if request["status"] != "returned":
            raise BusinessError("当前状态不允许确认收货")

        if request["type"] == "exchange":
            # 换货：收到退货后进入等待重新发货状态
            cur.execute(
                "UPDATE shop.after_sale_requests "
                "SET status = 'resend', return_status = 'received', "
                "received_at = NOW(), updated_at = NOW() "
                "WHERE id = %s RETURNING *",
                (after_sale_id,),
            )
        else:
            # 退货退款：收到退货后直接完成
            cur.execute(
                "UPDATE shop.after_sale_requests "
                "SET status = 'completed', return_status = 'received', "
                "received_at = NOW(), completed_at = NOW(), updated_at = NOW() "
                "WHERE id = %s RETURNING *",
                (after_sale_id,),
            )

        result = dict(cur.fetchone())
        format_date_fields(result, ("created_at", "updated_at", "received_at", "completed_at"))
        return result


def resend_exchange(after_sale_id: int, merchant_id: int, tracking_number: str, carrier: str = "SF-Express") -> dict:
    """商家填写换货物流（换货流程最后一步）"""
    _check_merchant_owner(after_sale_id, merchant_id)

    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s FOR UPDATE",
            (after_sale_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        request = dict(row)

        if request["status"] != "resend":
            raise BusinessError("当前状态不允许填写换货物流")
        if request["type"] != "exchange":
            raise BusinessError("仅换货类型的售后可填写换货物流")

        cur.execute(
            "UPDATE shop.after_sale_requests "
            "SET status = 'completed', resend_tracking_number = %s, resend_carrier = %s, "
            "completed_at = NOW(), updated_at = NOW() "
            "WHERE id = %s RETURNING *",
            (tracking_number, carrier, after_sale_id),
        )
        result = dict(cur.fetchone())
        format_date_fields(result, ("created_at", "updated_at", "completed_at"))
        return result


def delete_after_sale(after_sale_id: int) -> dict:
    """管理员删除售后记录"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s",
            (after_sale_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        record = dict(row)

        cur.execute("DELETE FROM shop.after_sale_requests WHERE id = %s", (after_sale_id,))

    logger.info("售后记录已删除 | after_sale_id=%s", after_sale_id)
    return record


def cancel_after_sale(after_sale_id: int, user_id: int) -> dict:
    """用户取消自己的售后申请（仅 pending 状态可取消）"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.after_sale_requests WHERE id = %s AND user_id = %s",
            (after_sale_id, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("售后申请不存在")
        request = dict(row)

        if request["status"] != "pending":
            raise BusinessError("仅待处理状态的售后申请可以取消")

        cur.execute(
            "UPDATE shop.after_sale_requests SET status = 'cancelled', updated_at = NOW() "
            "WHERE id = %s RETURNING *",
            (after_sale_id,),
        )
        result = dict(cur.fetchone())
        format_date_fields(result, ("created_at", "updated_at"))

    logger.info("售后申请已取消 | after_sale_id=%s user_id=%s", after_sale_id, user_id)
    return result
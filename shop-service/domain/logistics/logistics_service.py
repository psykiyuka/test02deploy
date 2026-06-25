import logging
import json
from datetime import datetime, timedelta

from infrastructure.database import get_cursor, get_connection, release_connection
from common.exceptions import NotFoundError, BusinessError
from common.utils import format_date_fields

logger = logging.getLogger("shop")

# 正向物流状态流转：pending → picked_up → in_transit → out_for_delivery → delivered
# 注：returned 状态仅用于售后退货场景，不在正向物流流转中出现
VALID_LOGISTICS_STATUSES = ["pending", "picked_up", "in_transit", "out_for_delivery", "delivered"]

STATUS_TRANSITIONS = {
    "pending": ["picked_up"],
    "picked_up": ["in_transit"],
    "in_transit": ["out_for_delivery"],
    "out_for_delivery": ["delivered"],
    "delivered": [],
}

LOCATION_MAP = {
    "pending": "仓库准备中",
    "picked_up": "已从仓库发出",
    "in_transit": "运输中",
    "out_for_delivery": "派送中",
    "delivered": "已送达",
}


def get_logistics(user_id: int, order_id: int = None) -> list:
    if order_id:
        with get_cursor() as cur:
            cur.execute(
                "SELECT lr.* FROM shop.logistics_records lr "
                "JOIN shop.orders o ON lr.order_id = o.id "
                "WHERE lr.order_id = %s AND o.user_id = %s",
                (order_id, user_id),
            )
            row = cur.fetchone()
            if not row:
                raise NotFoundError("物流信息不存在")
            record = dict(row)
            format_date_fields(record, ("created_at", "updated_at", "estimated_delivery"))
            if isinstance(record.get("timeline"), str):
                record["timeline"] = json.loads(record["timeline"])
            return [record]

    with get_cursor() as cur:
        cur.execute(
            "SELECT lr.* FROM shop.logistics_records lr "
            "JOIN shop.orders o ON lr.order_id = o.id "
            "WHERE o.user_id = %s ORDER BY lr.created_at DESC",
            (user_id,),
        )
        records = []
        for row in cur.fetchall():
            record = dict(row)
            format_date_fields(record, ("created_at", "updated_at", "estimated_delivery"))
            if isinstance(record.get("timeline"), str):
                record["timeline"] = json.loads(record["timeline"])
            records.append(record)
        return records


def generate_logistics(order_id: int):
    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM shop.logistics_records WHERE order_id = %s", (order_id,))
            if cur.fetchone():
                return

            tracking_number = f"SF{order_id:08d}"
            estimated_delivery = datetime.utcnow() + timedelta(days=3)

            timeline = json.dumps([
                {"time": datetime.utcnow().isoformat(), "status": "picked_up", "location": "深圳分拣中心"},
            ], ensure_ascii=False)

            cur.execute(
                "INSERT INTO shop.logistics_records (order_id, tracking_number, carrier, status, "
                "current_location, estimated_delivery, timeline) "
                "VALUES (%s, %s, 'SF-Express', 'picked_up', '深圳分拣中心', %s, %s)",
                (order_id, tracking_number, estimated_delivery, timeline),
            )

        conn.commit()
        logger.info("物流记录已生成 | order_id=%s | tracking=%s", order_id, tracking_number)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True
        release_connection(conn)
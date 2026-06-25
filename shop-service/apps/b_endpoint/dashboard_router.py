from fastapi import APIRouter, Depends

from apps.common.auth import get_current_admin
from infrastructure.database import get_cursor

router = APIRouter(prefix="/b-endpoint/dashboard", tags=["B端-仪表盘"])

_DAY_NAMES = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]


@router.get("/stats")
def b_get_dashboard_stats(admin: dict = Depends(get_current_admin)):
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as total FROM shop.orders")
        total_orders = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) as total FROM shop.products")
        total_products = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) as total FROM shop.after_sale_requests WHERE status = 'pending'")
        pending_after_sales = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) as total FROM shop.categories")
        total_categories = cur.fetchone()["total"]

        cur.execute("SELECT COALESCE(SUM(total_amount), 0) as total FROM shop.orders WHERE status = 'paid'")
        total_revenue = float(cur.fetchone()["total"])

        cur.execute("SELECT COUNT(*) as total FROM shop.users")
        total_users = cur.fetchone()["total"]

        # 今日订单数
        cur.execute(
            "SELECT COUNT(*) as total FROM shop.orders "
            "WHERE created_at >= CURRENT_DATE"
        )
        today_orders = cur.fetchone()["total"]

        cur.execute(
            "SELECT o.id, o.total_amount, o.status, o.created_at, u.email, "
            "s.shop_name as merchant_shop_name "
            "FROM shop.orders o "
            "JOIN shop.users u ON o.user_id = u.id "
            "LEFT JOIN shop.users s ON o.merchant_id = s.id "
            "ORDER BY o.created_at DESC LIMIT 5"
        )
        recent_orders = [dict(row) for row in cur.fetchall()]

    return {
        "code": 0,
        "data": {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "total_products": total_products,
            "pending_after_sales": pending_after_sales,
            "total_categories": total_categories,
            "total_revenue": total_revenue,
            "total_users": total_users,
            "recent_orders": recent_orders,
        },
        "message": "success",
    }


@router.get("/sales-trend")
def b_get_sales_trend(admin: dict = Depends(get_current_admin)):
    """最近7天每日已支付订单销售额走势"""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                d::date AS day,
                COALESCE(SUM(o.total_amount), 0) AS total
            FROM generate_series(
                CURRENT_DATE - INTERVAL '6 days',
                CURRENT_DATE,
                INTERVAL '1 day'
            ) AS d
            LEFT JOIN shop.orders o
                ON o.created_at >= d::date
               AND o.created_at <  d::date + INTERVAL '1 day'
               AND o.status = 'paid'
            GROUP BY d::date
            ORDER BY d::date
            """
        )
        rows = cur.fetchall()

    trend = []
    for row in rows:
        day = row["day"]
        total = float(row["total"])
        trend.append({
            "date": day.isoformat() if hasattr(day, "isoformat") else str(day),
            "label": _DAY_NAMES[day.weekday()] if hasattr(day, "weekday") else "",
            "total": total,
        })

    return {
        "code": 0,
        "data": {"trend": trend},
        "message": "success",
    }
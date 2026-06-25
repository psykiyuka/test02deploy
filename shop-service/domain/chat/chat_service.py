"""
人工客服聊天 service
处理会话创建、消息发送、消息查询等业务逻辑
"""
import logging
from typing import List, Optional, Dict

logger = logging.getLogger("shop")

from infrastructure.database import get_cursor


def create_or_get_session(buyer_id: int, merchant_id: Optional[int] = None, product_id: Optional[int] = None) -> Dict:
    """
    创建或获取聊天会话
    路由逻辑：
      - 有 product_id → 查商品所属商家，merchant_id 填入
      - 无 product_id → merchant_id = None（系统级，管理员处理）
    同一个 buyer 对同一个 merchant（或系统级）只保留一个 active 会话
    """
    with get_cursor() as cur:
        if product_id is not None:
            # 查商品所属商家
            cur.execute("SELECT merchant_id FROM shop.products WHERE id = %s", (product_id,))
            row = cur.fetchone()
            if row and row["merchant_id"]:
                merchant_id = row["merchant_id"]

        # 查找是否已有 active 会话
        if merchant_id is not None:
            cur.execute(
                "SELECT id, status FROM customer_service.chat_sessions "
                "WHERE buyer_id = %s AND merchant_id = %s AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1",
                (buyer_id, merchant_id),
            )
        else:
            cur.execute(
                "SELECT id, status FROM customer_service.chat_sessions "
                "WHERE buyer_id = %s AND merchant_id IS NULL AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1",
                (buyer_id,),
            )

        row = cur.fetchone()
        if row:
            logger.info(f"[Chat] 复用会话：session_id={row['id']}")
            # 查接收方信息
            receiver_type, receiver_name = _get_receiver_info(cur, merchant_id)
            return {"session_id": row["id"], "receiver_type": receiver_type, "receiver_name": receiver_name, "status": row["status"]}

        # 创建新会话
        cur.execute(
            "INSERT INTO customer_service.chat_sessions (buyer_id, merchant_id, product_id, status) "
            "VALUES (%s, %s, %s, 'active') RETURNING id",
            (buyer_id, merchant_id, product_id),
        )
        session_id = cur.fetchone()["id"]
        logger.info(f"[Chat] 创建新会话：session_id={session_id}, buyer={buyer_id}, merchant={merchant_id}")
        # 查接收方信息
        receiver_type, receiver_name = _get_receiver_info(cur, merchant_id)
        return {"session_id": session_id, "receiver_type": receiver_type, "receiver_name": receiver_name, "status": "active"}


def _get_receiver_info(cur, merchant_id: Optional[int]):
    """获取接收方类型和名称"""
    if merchant_id is not None:
        cur.execute("SELECT nickname, shop_name FROM shop.users WHERE id = %s", (merchant_id,))
        row = cur.fetchone()
        if row:
            # 优先显示店铺名，没有的话用昵称
            name = row["shop_name"] if row["shop_name"] else row["nickname"]
            return ("merchant", name)
        return ("merchant", "商家")
    else:
        return ("admin", "平台管理员")


def send_message(session_id: int, sender_id: int, sender_role: str, message: str) -> Dict:
    """发送消息"""
    with get_cursor() as cur:
        # 验证会话存在且调用方有权限
        if sender_role == "buyer":
            cur.execute(
                "SELECT id FROM customer_service.chat_sessions WHERE id = %s AND buyer_id = %s",
                (session_id, sender_id),
            )
        elif sender_role == "merchant":
            cur.execute(
                "SELECT id FROM customer_service.chat_sessions WHERE id = %s AND merchant_id = %s",
                (session_id, sender_id),
            )
        else:
            # admin 只能回复系统级会话（merchant_id IS NULL）
            cur.execute(
                "SELECT id FROM customer_service.chat_sessions WHERE id = %s AND merchant_id IS NULL",
                (session_id,),
            )
        if not cur.fetchone():
            raise ValueError("会话不存在或无权限")

        cur.execute(
            "INSERT INTO customer_service.chat_messages (session_id, sender_id, sender_role, message) "
            "VALUES (%s, %s, %s, %s) RETURNING id, created_at",
            (session_id, sender_id, sender_role, message),
        )
        row = cur.fetchone()

        # 更新会话的 updated_at
        cur.execute("UPDATE customer_service.chat_sessions SET updated_at = NOW() WHERE id = %s", (session_id,))

        logger.info(f"[Chat] 消息发送：session_id={session_id}, sender={sender_role}, msg_id={row['id']}")
        return {"message_id": row["id"], "created_at": row["created_at"]}


def get_session_messages(session_id: int, after_id: Optional[int] = None, reader_id: Optional[int] = None, reader_role: Optional[str] = None) -> List[Dict]:
    """
    获取会话消息
    after_id: 只获取 ID 大于 after_id 的消息（用于轮询新消息）
    reader_id + reader_role: 用于验证调用方有权限访问该会话
    """
    with get_cursor() as cur:
        # 验证权限
        if reader_role == "buyer" and reader_id is not None:
            cur.execute(
                "SELECT id FROM customer_service.chat_sessions WHERE id = %s AND buyer_id = %s",
                (session_id, reader_id),
            )
            if not cur.fetchone():
                raise ValueError("会话不存在或无权限")
        elif reader_role == "merchant" and reader_id is not None:
            cur.execute(
                "SELECT id FROM customer_service.chat_sessions WHERE id = %s AND merchant_id = %s",
                (session_id, reader_id),
            )
            if not cur.fetchone():
                raise ValueError("会话不存在或无权限")
        elif reader_role == "admin":
            cur.execute(
                "SELECT id FROM customer_service.chat_sessions WHERE id = %s AND merchant_id IS NULL",
                (session_id,),
            )
            if not cur.fetchone():
                raise ValueError("会话不存在或无权限")

        if after_id is not None:
            cur.execute(
                "SELECT id, sender_id, sender_role, message, is_read, created_at "
                "FROM customer_service.chat_messages "
                "WHERE session_id = %s AND id > %s ORDER BY id ASC",
                (session_id, after_id),
            )
        else:
            cur.execute(
                "SELECT id, sender_id, sender_role, message, is_read, created_at "
                "FROM customer_service.chat_messages "
                "WHERE session_id = %s ORDER BY id ASC",
                (session_id,),
            )
        return [dict(r) for r in cur.fetchall()]


def mark_messages_read(session_id: int, reader_role: str) -> None:
    """
    标记消息已读
    将会话中 sender_role != reader_role 的未读消息标记为已读
    """
    with get_cursor() as cur:
        cur.execute(
            "UPDATE customer_service.chat_messages SET is_read = TRUE "
            "WHERE session_id = %s AND sender_role != %s AND is_read = FALSE",
            (session_id, reader_role),
        )
        logger.info(f"[Chat] 标记已读：session_id={session_id}, reader={reader_role}")


def get_buyer_sessions(buyer_id: int) -> List[Dict]:
    """获取买家的所有会话列表"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT s.id, s.merchant_id, s.product_id, s.status, s.updated_at, "
            "  (SELECT message FROM customer_service.chat_messages WHERE session_id = s.id ORDER BY id DESC LIMIT 1) AS last_message, "
            "  (SELECT COUNT(*) FROM customer_service.chat_messages WHERE session_id = s.id AND sender_role = 'merchant' AND is_read = FALSE) AS unread_count "
            "FROM customer_service.chat_sessions s "
            "WHERE s.buyer_id = %s ORDER BY s.updated_at DESC",
            (buyer_id,),
        )
        return [dict(r) for r in cur.fetchall()]


def get_merchant_sessions(merchant_id: int) -> List[Dict]:
    """获取商家的所有会话列表（用于卖家端）"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT s.id, s.buyer_id, s.product_id, s.status, s.updated_at, "
            "  u.nickname AS buyer_name, "
            "  p.name AS product_name, "
            "  (SELECT message FROM customer_service.chat_messages WHERE session_id = s.id ORDER BY id DESC LIMIT 1) AS last_message, "
            "  (SELECT COUNT(*) FROM customer_service.chat_messages WHERE session_id = s.id AND sender_role = 'buyer' AND is_read = FALSE) AS unread_count "
            "FROM customer_service.chat_sessions s "
            "LEFT JOIN shop.users u ON u.id = s.buyer_id "
            "LEFT JOIN shop.products p ON p.id = s.product_id "
            "WHERE s.merchant_id = %s ORDER BY s.updated_at DESC",
            (merchant_id,),
        )
        return [dict(r) for r in cur.fetchall()]


def get_admin_sessions() -> List[Dict]:
    """获取系统级会话列表（用于管理员端）"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT s.id, s.buyer_id, s.product_id, s.status, s.updated_at, "
            "  u.nickname AS buyer_name, "
            "  p.name AS product_name, "
            "  (SELECT message FROM customer_service.chat_messages WHERE session_id = s.id ORDER BY id DESC LIMIT 1) AS last_message, "
            "  (SELECT COUNT(*) FROM customer_service.chat_messages WHERE session_id = s.id AND sender_role = 'buyer' AND is_read = FALSE) AS unread_count "
            "FROM customer_service.chat_sessions s "
            "LEFT JOIN shop.users u ON u.id = s.buyer_id "
            "LEFT JOIN shop.products p ON p.id = s.product_id "
            "WHERE s.merchant_id IS NULL ORDER BY s.updated_at DESC",
        )
        return [dict(r) for r in cur.fetchall()]


def close_session(session_id: int, buyer_id: int) -> None:
    """关闭会话（买家操作）"""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE customer_service.chat_sessions SET status = 'closed' WHERE id = %s AND buyer_id = %s",
            (session_id, buyer_id),
        )
        if cur.rowcount == 0:
            raise ValueError("会话不存在或无权限")
        logger.info(f"[Chat] 会话关闭：session_id={session_id}")

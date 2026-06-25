import logging

from infrastructure.database import get_cursor, get_connection, release_connection
from common.exceptions import NotFoundError, BusinessError
from common.utils import format_date_fields

logger = logging.getLogger("shop")


def get_addresses(user_id: int) -> list:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM shop.user_addresses WHERE user_id = %s ORDER BY is_default DESC, created_at DESC",
            (user_id,),
        )
        addresses = [dict(row) for row in cur.fetchall()]
        for addr in addresses:
            format_date_fields(addr, ("created_at", "updated_at"))
        return addresses


def add_address(user_id: int, name: str, phone: str, province: str, city: str,
               district: str, detail: str, is_default: bool = False) -> dict:
    if not name or not phone or not detail:
        raise BusinessError("收件人、手机号和详细地址不能为空")

    with get_cursor() as cur:
        # 如果是默认地址，先取消其他默认
        if is_default:
            cur.execute(
                "UPDATE shop.user_addresses SET is_default = FALSE WHERE user_id = %s",
                (user_id,),
            )

        # 如果是第一个地址，自动设为默认
        cur.execute("SELECT COUNT(*) as cnt FROM shop.user_addresses WHERE user_id = %s", (user_id,))
        count = cur.fetchone()["cnt"]
        if count == 0:
            is_default = True

        cur.execute(
            "INSERT INTO shop.user_addresses (user_id, name, phone, province, city, district, detail, is_default) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
            (user_id, name, phone, province, city, district, detail, is_default),
        )
        row = cur.fetchone()
        if not row:
            raise BusinessError("添加地址失败")
        result = dict(row)

    format_date_fields(result, ("created_at", "updated_at"))
    logger.info("地址已添加 | user_id=%s | name=%s", user_id, name)
    return result


def update_address(address_id: int, user_id: int, name: str = None, phone: str = None,
                  province: str = None, city: str = None, district: str = None,
                  detail: str = None, is_default: bool = None) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM shop.user_addresses WHERE id = %s AND user_id = %s", (address_id, user_id))
        if not cur.fetchone():
            raise NotFoundError("地址不存在")

        updates = []
        params = []
        for field, value in [("name", name), ("phone", phone), ("province", province),
                            ("city", city), ("district", district), ("detail", detail)]:
            if value is not None:
                updates.append(f"{field} = %s")
                params.append(value)

        if not updates and is_default is None:
            raise BusinessError("没有需要更新的字段")

        # 如果设为默认
        if is_default:
            cur.execute("UPDATE shop.user_addresses SET is_default = FALSE WHERE user_id = %s", (user_id,))

        if is_default is not None:
            updates.append("is_default = %s")
            params.append(is_default)

        updates.append("updated_at = NOW()")
        params.extend([address_id, user_id])

        cur.execute(
            f"UPDATE shop.user_addresses SET {', '.join(updates)} WHERE id = %s AND user_id = %s RETURNING *",
            params,
        )
        result = dict(cur.fetchone())

    format_date_fields(result, ("created_at", "updated_at"))
    return result


def delete_address(address_id: int, user_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM shop.user_addresses WHERE id = %s AND user_id = %s", (address_id, user_id))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("地址不存在")
        addr = dict(row)

        cur.execute("DELETE FROM shop.user_addresses WHERE id = %s", (address_id,))

        # 如果删除的是默认地址，把第一个设为默认
        if addr["is_default"]:
            cur.execute(
                "UPDATE shop.user_addresses SET is_default = TRUE WHERE user_id = %s "
                "ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            )

    logger.info("地址已删除 | address_id=%s | user_id=%s", address_id, user_id)
    return addr


def set_default_address(address_id: int, user_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM shop.user_addresses WHERE id = %s AND user_id = %s", (address_id, user_id))
        if not cur.fetchone():
            raise NotFoundError("地址不存在")

        cur.execute("UPDATE shop.user_addresses SET is_default = FALSE WHERE user_id = %s", (user_id,))
        cur.execute(
            "UPDATE shop.user_addresses SET is_default = TRUE, updated_at = NOW() WHERE id = %s RETURNING *",
            (address_id,),
        )
        result = dict(cur.fetchone())

    format_date_fields(result, ("created_at", "updated_at"))
    return result

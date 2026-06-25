import logging
import re
import random
import string

from infrastructure.database import get_cursor
from infrastructure.redis_client import get_cache, set_cache, delete_cache
from common.exceptions import ValidationError, AuthenticationError, NotFoundError
from apps.common.auth import hash_password, verify_password, create_token

logger = logging.getLogger("shop")

_login_attempts: dict[str, list[float]] = {}
_LOGIN_MAX_ATTEMPTS = 5
_LOGIN_LOCK_MINUTES = 15


def _check_rate_limit(email: str):
    import time
    now = time.time()
    attempts = _login_attempts.get(email, [])
    attempts = [t for t in attempts if now - t < _LOGIN_LOCK_MINUTES * 60]
    _login_attempts[email] = attempts
    if len(attempts) >= _LOGIN_MAX_ATTEMPTS:
        raise AuthenticationError("登录尝试过多，请15分钟后再试")


def _record_failed_attempt(email: str):
    import time
    attempts = _login_attempts.get(email, [])
    attempts.append(time.time())
    _login_attempts[email] = attempts


def _validate_password_strength(password: str):
    if len(password) < 8:
        raise ValidationError("密码长度不能少于8位")
    if not re.search(r'[A-Za-z]', password):
        raise ValidationError("密码必须包含至少一个字母")
    if not re.search(r'\d', password):
        raise ValidationError("密码必须包含至少一个数字")


def register_user(email: str, password: str, nickname: str, role: str = "user", shop_name: str = None, business_category: str = None, business_license: str = None, id_card: str = None, security_question: str = None, security_answer: str = None) -> dict:
    _validate_password_strength(password)

    with get_cursor() as cur:
        cur.execute("SELECT id FROM shop.users WHERE email = %s", (email,))
        if cur.fetchone():
            raise ValidationError("该邮箱已注册")

        hashed = hash_password(password)
        answer_hashed = hash_password(security_answer) if security_answer else None
        
        if role == "merchant":
            cur.execute(
                "INSERT INTO shop.users (email, password, nickname, role, merchant_status, shop_name, business_category, business_license, id_card, security_question, security_answer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, email, nickname, role, merchant_status, shop_name, created_at",
                (email, hashed, nickname, "merchant", "pending", shop_name, business_category, business_license, id_card, security_question, answer_hashed),
            )
        else:
            cur.execute(
                "INSERT INTO shop.users (email, password, nickname, role, merchant_status, security_question, security_answer) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, email, nickname, role, merchant_status, created_at",
                (email, hashed, nickname, role, "approved", security_question, answer_hashed),
            )
        user = dict(cur.fetchone())
        user.pop("password", None)
        return user


def login_user(email: str, password: str) -> dict:
    _check_rate_limit(email)

    with get_cursor() as cur:
        cur.execute("SELECT id, email, password, nickname, role, merchant_status FROM shop.users WHERE email = %s", (email,))
        row = cur.fetchone()
        if not row:
            _record_failed_attempt(email)
            raise AuthenticationError("邮箱或密码错误")

        user = dict(row)
        if not verify_password(password, user["password"]):
            _record_failed_attempt(email)
            raise AuthenticationError("邮箱或密码错误")

        _login_attempts.pop(email, None)

        token = create_token(user["id"], user["email"], user["role"])
        return {
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "nickname": user["nickname"],
                "role": user["role"],
                "merchant_status": user.get("merchant_status"),
            },
        }


def get_user_profile(user_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT id, email, nickname, role, address, merchant_status, shop_name, shop_description, shop_logo, reject_reason, avatar_url, created_at FROM shop.users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def refresh_token(user_id: int) -> dict:
    """从数据库取最新用户信息，重新生成token"""
    with get_cursor() as cur:
        cur.execute("SELECT id, email, nickname, role, merchant_status FROM shop.users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        user = dict(row)
    token = create_token(user["id"], user["email"], user["role"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "role": user["role"],
            "merchant_status": user.get("merchant_status"),
        },
    }


def update_user_address(user_id: int, address: str) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.users SET address = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role, address",
            (address, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def update_user_nickname(user_id: int, nickname: str) -> dict:
    if not nickname or len(nickname.strip()) == 0:
        raise ValidationError("昵称不能为空")
    if len(nickname) > 50:
        raise ValidationError("昵称长度不能超过50个字符")
    
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.users SET nickname = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role",
            (nickname.strip(), user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def change_password(user_id: int, old_password: str, new_password: str) -> dict:
    _validate_password_strength(new_password)
    
    with get_cursor() as cur:
        cur.execute("SELECT password FROM shop.users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        
        if not verify_password(old_password, row["password"]):
            raise AuthenticationError("原密码不正确")
        
        hashed = hash_password(new_password)
        cur.execute(
            "UPDATE shop.users SET password = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role",
            (hashed, user_id),
        )
        row = cur.fetchone()
        return dict(row)


def update_avatar(user_id: int, avatar_url: str) -> dict:
    """更新用户头像 URL"""
    if not avatar_url:
        raise ValidationError("头像地址不能为空")
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.users SET avatar_url = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role, avatar_url",
            (avatar_url, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def update_shop_info(user_id: int, shop_name: str, shop_description: str = None, shop_logo: str = None) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.users SET shop_name = %s, shop_description = %s, shop_logo = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role, shop_name, shop_description, shop_logo",
            (shop_name, shop_description, shop_logo, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def approve_merchant(user_id: int) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.users SET merchant_status = 'approved', updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role, merchant_status, shop_name",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def reject_merchant(user_id: int, reason: str = None) -> dict:
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.users SET merchant_status = 'rejected', reject_reason = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role, merchant_status, shop_name, reject_reason",
            (reason, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def reset_password(user_id: int, new_password: str) -> dict:
    _validate_password_strength(new_password)
    hashed = hash_password(new_password)
    
    with get_cursor() as cur:
        cur.execute(
            "UPDATE shop.users SET password = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role",
            (hashed, user_id),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        return dict(row)


def get_all_users(page: int = 1, size: int = 20, role: str = None, merchant_status: str = None) -> dict:
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = []
    params = []
    
    if role:
        conditions.append("role = %s")
        params.append(role)
    if merchant_status:
        conditions.append("merchant_status = %s")
        params.append(merchant_status)
    
    where = " AND ".join(conditions) if conditions else "1=1"
    
    with get_cursor() as cur:
        cur.execute(
            f"SELECT COUNT(*) as total FROM shop.users WHERE {where}",
            params,
        )
        total = cur.fetchone()["total"]
        
        cur.execute(
            f"SELECT id, email, nickname, role, merchant_status, shop_name, created_at FROM shop.users WHERE {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params + [size, offset],
        )
        items = [dict(row) for row in cur.fetchall()]
    
    return {"items": items, "total": total, "page": page, "size": size}


def delete_user(user_id: int) -> dict:
    """管理员删除用户，级联清理关联数据"""
    with get_cursor() as cur:
        cur.execute("SELECT id, email, role FROM shop.users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        user = dict(row)

        if user["role"] == "admin":
            raise ValidationError("不能删除管理员账号")

        # 级联清理
        cur.execute("DELETE FROM shop.cart_items WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM shop.user_favorites WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM shop.order_items WHERE order_id IN (SELECT id FROM shop.orders WHERE user_id = %s)", (user_id,))
        cur.execute("DELETE FROM shop.orders WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM shop.after_sale_requests WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM shop.products WHERE merchant_id = %s", (user_id,))
        cur.execute("DELETE FROM shop.users WHERE id = %s", (user_id,))

    logger.info("用户已删除 | user_id=%s email=%s", user_id, user["email"])
    return user


# ========== 邮箱换绑申请 ==========

def apply_email_change(user_id: int, new_email: str) -> dict:
    """用户提交换绑邮箱申请"""
    with get_cursor() as cur:
        # 检查新邮箱是否已被占用
        cur.execute("SELECT id FROM shop.users WHERE email = %s AND id != %s", (new_email, user_id))
        if cur.fetchone():
            raise ValidationError("该邮箱已被使用")

        # 获取旧邮箱
        cur.execute("SELECT email FROM shop.users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")
        old_email = row["email"]

        if old_email == new_email:
            raise ValidationError("新邮箱不能与当前邮箱相同")

        # 关闭该用户已有的 pending 申请
        cur.execute(
            "UPDATE shop.email_change_requests SET status = 'cancelled' WHERE user_id = %s AND status = 'pending'",
            (user_id,)
        )

        # 插入新申请
        cur.execute(
            """INSERT INTO shop.email_change_requests (user_id, old_email, new_email, status)
               VALUES (%s, %s, %s, 'pending') RETURNING id, user_id, old_email, new_email, status, created_at""",
            (user_id, old_email, new_email),
        )
        return dict(cur.fetchone())


def get_email_change_requests(page: int = 1, size: int = 20, status: str = None) -> dict:
    """管理员查看邮箱换绑申请列表"""
    size = min(max(size, 1), 100)
    offset = (page - 1) * size
    conditions = []
    params = []

    if status:
        conditions.append("ecr.status = %s")
        params.append(status)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_cursor() as cur:
        cur.execute(
            f"""SELECT COUNT(*) AS cnt FROM shop.email_change_requests ecr {where}""",
            params,
        )
        total = cur.fetchone()["cnt"]

        cur.execute(
            f"""SELECT ecr.id, ecr.user_id, ecr.old_email, ecr.new_email, ecr.status,
                      ecr.reject_reason, ecr.created_at, u.nickname, u.shop_name
               FROM shop.email_change_requests ecr
               LEFT JOIN shop.users u ON u.id = ecr.user_id
               {where}
               ORDER BY ecr.created_at DESC
               LIMIT %s OFFSET %s""",
            params + [size, offset],
        )
        items = [dict(row) for row in cur.fetchall()]

    return {"items": items, "total": total, "page": page, "size": size}


def approve_email_change(request_id: int) -> dict:
    """管理员通过邮箱换绑申请，更新用户邮箱"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT user_id, new_email, status FROM shop.email_change_requests WHERE id = %s",
            (request_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("申请不存在")
        if row["status"] != "pending":
            raise ValidationError("该申请已处理")

        # 更新用户邮箱
        cur.execute(
            "UPDATE shop.users SET email = %s, updated_at = NOW() WHERE id = %s",
            (row["new_email"], row["user_id"]),
        )
        # 更新申请状态
        cur.execute(
            "UPDATE shop.email_change_requests SET status = 'approved', updated_at = NOW() WHERE id = %s",
            (request_id,),
        )
        return {"email": row["new_email"]}


def reject_email_change(request_id: int, reason: str = None) -> dict:
    """管理员拒绝邮箱换绑申请"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT status FROM shop.email_change_requests WHERE id = %s",
            (request_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("申请不存在")
        if row["status"] != "pending":
            raise ValidationError("该申请已处理")

        cur.execute(
            "UPDATE shop.email_change_requests SET status = 'rejected', reject_reason = %s, updated_at = NOW() WHERE id = %s",
            (reason, request_id),
        )
        return {"status": "rejected"}


# ========== 忘记密码（安全问题） ==========


def get_security_question(email: str) -> dict:
    """根据邮箱获取用户的安全问题"""
    email = email.strip().lower()
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, security_question FROM shop.users WHERE email = %s",
            (email,)
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("该邮箱未注册")
        if not row["security_question"]:
            raise ValidationError("该账户未设置安全问题，请联系管理员重置密码")
        return {"email": email, "question": row["security_question"]}


def verify_security_answer(email: str, answer: str) -> dict:
    """仅验证安全问题答案是否正确，不重置密码"""
    email = email.strip().lower()

    with get_cursor() as cur:
        cur.execute(
            "SELECT id, security_answer FROM shop.users WHERE email = %s",
            (email,)
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")

        if not row["security_answer"]:
            raise ValidationError("该账户未设置安全问题")

        if not verify_password(answer.strip(), row["security_answer"]):
            raise ValidationError("安全问题答案不正确")

    return {"ok": True}


def reset_password_by_answer(email: str, answer: str, new_password: str) -> dict:
    """通过安全问题答案重置密码"""
    email = email.strip().lower()
    _validate_password_strength(new_password)

    with get_cursor() as cur:
        cur.execute(
            "SELECT id, security_answer FROM shop.users WHERE email = %s",
            (email,)
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError("用户不存在")

        if not row["security_answer"]:
            raise ValidationError("该账户未设置安全问题")

        # 验证答案（bcrypt 比对）
        if not verify_password(answer.strip(), row["security_answer"]):
            raise ValidationError("安全问题答案不正确")

        hashed = hash_password(new_password)
        cur.execute(
            "UPDATE shop.users SET password = %s, updated_at = NOW() WHERE id = %s RETURNING id, email, nickname, role",
            (hashed, row["id"]),
        )
        result = dict(cur.fetchone())

    logger.info("密码已通过安全问题重置 | email=%s", email)
    return result
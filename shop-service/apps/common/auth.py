import os
import hmac
from datetime import datetime, timedelta, timezone

import jwt
import bcrypt
from fastapi import Header, Depends

from common.exceptions import AuthenticationError, PermissionDeniedError

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "dev-internal-token")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def get_current_user(authorization: str = Header(None)) -> dict:
    if not authorization:
        raise AuthenticationError("未登录或Token过期")

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise AuthenticationError("Authorization格式错误，应为Bearer <token>")
    except ValueError:
        raise AuthenticationError("Authorization格式错误，应为Bearer <token>")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {
            "user_id": payload["user_id"],
            "email": payload["email"],
            "role": payload["role"],
        }
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token已过期")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Token无效")


def get_current_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise PermissionDeniedError("需要管理员权限")
    return user


def get_current_merchant(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "merchant":
        raise PermissionDeniedError("需要商家权限")
    # 从数据库校验 merchant_status
    from infrastructure.database import get_cursor
    with get_cursor() as cur:
        cur.execute("SELECT merchant_status FROM shop.users WHERE id = %s", (user["user_id"],))
        row = cur.fetchone()
        if not row or row["merchant_status"] != "approved":
            raise PermissionDeniedError("商家账号未通过审核")
    return user


def verify_internal_token(x_internal_token: str = Header(..., alias="X-Internal-Token")) -> bool:
    if not hmac.compare_digest(x_internal_token, INTERNAL_API_TOKEN):
        raise AuthenticationError("无效的内部接口Token")
    return True
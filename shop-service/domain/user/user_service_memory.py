import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext

SECRET_KEY = "shop_secret_key_123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 内存用户存储
users_db: Dict[str, dict] = {
    "admin@test.com": {
        "id": 1,
        "email": "admin@test.com",
        "password": pwd_context.hash("12345678"),
        "nickname": "管理员",
        "role": "admin",
        "created_at": datetime.now().isoformat()
    },
    "user@test.com": {
        "id": 2,
        "email": "user@test.com",
        "password": pwd_context.hash("12345678"),
        "nickname": "普通用户",
        "role": "user",
        "created_at": datetime.now().isoformat()
    },
    "merchant@test.com": {
        "id": 3,
        "email": "merchant@test.com",
        "password": pwd_context.hash("12345678"),
        "nickname": "商家",
        "role": "merchant",
        "shop_name": "测试店铺",
        "created_at": datetime.now().isoformat()
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_user(email: str, password: str) -> dict:
    user = users_db.get(email)
    if not user:
        raise Exception({"code": 1001, "message": "邮箱或密码错误"})
    
    if not verify_password(password, user["password"]):
        raise Exception({"code": 1002, "message": "邮箱或密码错误"})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email, "user_id": user["id"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "nickname": user["nickname"],
            "role": user["role"]
        }
    }

def register_user(email: str, password: str, nickname: str, role: str = "user", shop_name: str = "") -> dict:
    if email in users_db:
        raise Exception({"code": 1003, "message": "该邮箱已注册"})
    
    user_id = len(users_db) + 1
    new_user = {
        "id": user_id,
        "email": email,
        "password": pwd_context.hash(password),
        "nickname": nickname,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    if role == "merchant":
        new_user["shop_name"] = shop_name
    
    users_db[email] = new_user
    
    return {
        "id": user_id,
        "email": email,
        "nickname": nickname,
        "role": role
    }

def get_user_profile(user_id: int) -> dict:
    for user in users_db.values():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "email": user["email"],
                "nickname": user["nickname"],
                "role": user["role"],
                "shop_name": user.get("shop_name", "")
            }
    raise Exception({"code": 1004, "message": "用户不存在"})

def update_user_nickname(user_id: int, nickname: str) -> dict:
    for user in users_db.values():
        if user["id"] == user_id:
            user["nickname"] = nickname
            return {"success": True}
    raise Exception({"code": 1004, "message": "用户不存在"})

def change_password(user_id: int, old_password: str, new_password: str) -> dict:
    for user in users_db.values():
        if user["id"] == user_id:
            if not verify_password(old_password, user["password"]):
                raise Exception({"code": 1005, "message": "原密码不正确"})
            user["password"] = pwd_context.hash(new_password)
            return {"success": True}
    raise Exception({"code": 1004, "message": "用户不存在"})

def update_user_address(user_id: int, address: str) -> dict:
    for user in users_db.values():
        if user["id"] == user_id:
            user["address"] = address
            return {"success": True}
    raise Exception({"code": 1004, "message": "用户不存在"})

def update_shop_info(user_id: int, shop_name: str, shop_description: str, shop_logo: str) -> dict:
    for user in users_db.values():
        if user["id"] == user_id:
            user["shop_name"] = shop_name
            user["shop_description"] = shop_description
            user["shop_logo"] = shop_logo
            return {"success": True}
    raise Exception({"code": 1004, "message": "用户不存在"})

def get_user_by_id(user_id: int) -> Optional[dict]:
    for user in users_db.values():
        if user["id"] == user_id:
            return user
    return None

def update_user_password(user_id: int, new_password: str) -> bool:
    for user in users_db.values():
        if user["id"] == user_id:
            user["password"] = pwd_context.hash(new_password)
            return True
    return False

def get_all_users() -> list:
    return [{
        "id": u["id"],
        "email": u["email"],
        "nickname": u["nickname"],
        "role": u["role"],
        "shop_name": u.get("shop_name", ""),
        "created_at": u.get("created_at", "")
    } for u in users_db.values()]

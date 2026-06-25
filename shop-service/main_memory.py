from fastapi import FastAPI, Depends, HTTPException, Response, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

SECRET_KEY = "shop_secret_key_123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nickname: str = Field(min_length=1, max_length=50)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UpdateNicknameRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=50)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)

class MerchantRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nickname: str = Field(min_length=1, max_length=50)
    shop_name: str = Field(min_length=1, max_length=100)

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

def get_current_user(token: str = Depends()) -> dict:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = users_db.get(email)
    if user is None:
        raise credentials_exception
    return {"user_id": user["id"], "email": user["email"], "role": user["role"]}

app = FastAPI(title="Shop Service - Memory Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_prefix = "/api/shop"

@app.post(f"{_prefix}/c-endpoint/user/register")
def c_register(req: RegisterRequest):
    if req.email in users_db:
        return {"code": 1003, "data": None, "message": "该邮箱已注册"}
    
    user_id = len(users_db) + 1
    users_db[req.email] = {
        "id": user_id,
        "email": req.email,
        "password": pwd_context.hash(req.password),
        "nickname": req.nickname,
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
    
    return {"code": 0, "data": {"id": user_id, "email": req.email, "nickname": req.nickname, "role": "user"}, "message": "success"}

@app.post(f"{_prefix}/c-endpoint/user/register/merchant")
async def c_register_merchant(
    email: str = Form(...),
    password: str = Form(...),
    nickname: str = Form(...),
    shop_name: str = Form(...),
    business_category: str = Form(None),
    business_license: UploadFile = File(None),
    id_card: UploadFile = File(None)
):
    if email in users_db:
        return {"code": 1003, "data": None, "message": "该邮箱已注册"}
    
    license_data = None
    id_card_data = None
    
    if business_license:
        content = await business_license.read()
        b64 = base64.b64encode(content).decode("utf-8")
        license_data = f"data:{business_license.content_type};base64,{b64}"
    
    if id_card:
        content = await id_card.read()
        b64 = base64.b64encode(content).decode("utf-8")
        id_card_data = f"data:{id_card.content_type};base64,{b64}"
    
    user_id = len(users_db) + 1
    users_db[email] = {
        "id": user_id,
        "email": email,
        "password": pwd_context.hash(password),
        "nickname": nickname,
        "role": "merchant",
        "shop_name": shop_name,
        "business_category": business_category,
        "business_license": license_data,
        "id_card": id_card_data,
        "merchant_status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    return {"code": 0, "data": {"id": user_id, "email": email, "nickname": nickname, "role": "merchant"}, "message": "注册成功，请等待管理员审核"}

@app.post(f"{_prefix}/c-endpoint/user/login")
def c_login(req: LoginRequest, response: Response):
    user = users_db.get(req.email)
    if not user:
        response_content = json.dumps({"code": 1001, "data": None, "message": "邮箱或密码错误"}, ensure_ascii=False)
        return Response(content=response_content, media_type="application/json; charset=utf-8")
    
    if not verify_password(req.password, user["password"]):
        response_content = json.dumps({"code": 1002, "data": None, "message": "邮箱或密码错误"}, ensure_ascii=False)
        return Response(content=response_content, media_type="application/json; charset=utf-8")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": req.email, "user_id": user["id"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    response_content = json.dumps({
        "code": 0, 
        "data": {
            "token": access_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "nickname": user["nickname"],
                "role": user["role"]
            }
        }, 
        "message": "登录成功"
    }, ensure_ascii=False)
    return Response(content=response_content, media_type="application/json; charset=utf-8")

@app.get(f"{_prefix}/c-endpoint/user/profile")
def c_get_profile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"code": 401, "data": None, "message": "未授权"}
    
    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return {"code": 401, "data": None, "message": "未授权"}
        
        for user in users_db.values():
            if user["id"] == user_id:
                response_content = json.dumps({
                    "code": 0, 
                    "data": {
                        "id": user["id"],
                        "email": user["email"],
                        "nickname": user["nickname"],
                        "role": user["role"],
                        "shop_name": user.get("shop_name", "")
                    }, 
                    "message": "success"
                }, ensure_ascii=False)
                return Response(content=response_content, media_type="application/json; charset=utf-8")
        
        return {"code": 1004, "data": None, "message": "用户不存在"}
    except jwt.PyJWTError:
        return {"code": 401, "data": None, "message": "登录已过期"}

@app.put(f"{_prefix}/c-endpoint/user/profile")
def c_update_profile(req: UpdateNicknameRequest, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"code": 401, "data": None, "message": "未授权"}
    
    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return {"code": 401, "data": None, "message": "未授权"}
        
        for user in users_db.values():
            if user["id"] == user_id:
                user["nickname"] = req.nickname
                response_content = json.dumps({"code": 0, "data": {"success": True}, "message": "修改成功"}, ensure_ascii=False)
                return Response(content=response_content, media_type="application/json; charset=utf-8")
        
        return {"code": 1004, "data": None, "message": "用户不存在"}
    except jwt.PyJWTError:
        return {"code": 401, "data": None, "message": "登录已过期"}

@app.put(f"{_prefix}/c-endpoint/user/password")
def c_change_password(req: ChangePasswordRequest, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"code": 401, "data": None, "message": "未授权"}
    
    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return {"code": 401, "data": None, "message": "未授权"}
        
        for user in users_db.values():
            if user["id"] == user_id:
                if not verify_password(req.old_password, user["password"]):
                    response_content = json.dumps({"code": 1005, "data": None, "message": "原密码不正确"}, ensure_ascii=False)
                    return Response(content=response_content, media_type="application/json; charset=utf-8")
                user["password"] = pwd_context.hash(req.new_password)
                response_content = json.dumps({"code": 0, "data": {"success": True}, "message": "修改成功"}, ensure_ascii=False)
                return Response(content=response_content, media_type="application/json; charset=utf-8")
        
        return {"code": 1004, "data": None, "message": "用户不存在"}
    except jwt.PyJWTError:
        return {"code": 401, "data": None, "message": "登录已过期"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "shop-service-memory"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=83)

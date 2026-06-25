import base64
from fastapi import APIRouter, Depends, UploadFile, File, Form

from apps.common.auth import get_current_user
from domain.user import register_user, login_user, get_user_profile, update_user_address, update_shop_info, update_user_nickname, change_password, update_avatar, apply_email_change, refresh_token, get_security_question, verify_security_answer, reset_password_by_answer
from common.exceptions import ValidationError
from .schema import RegisterRequest, LoginRequest, UpdateAddressRequest, MerchantRegisterRequest, UpdateShopInfoRequest, UpdateNicknameRequest, ChangePasswordRequest, EmailChangeApplyRequest, GetSecurityQuestionRequest, VerifySecurityAnswerRequest, ResetPasswordByAnswerRequest

router = APIRouter(prefix="/c-endpoint/user", tags=["C端-用户"])


@router.post("/register")
def c_register(req: RegisterRequest):
    user = register_user(req.email, req.password, req.nickname, security_question=req.security_question, security_answer=req.security_answer)
    return {"code": 0, "data": user, "message": "success"}


@router.post("/register/merchant")
async def c_register_merchant(
    email: str = Form(...),
    password: str = Form(...),
    nickname: str = Form(...),
    shop_name: str = Form(...),
    business_category: str = Form(None),
    security_question: str = Form("我最喜欢的食物"),
    security_answer: str = Form("番茄炒蛋"),
    business_license: UploadFile = File(None),
    id_card: UploadFile = File(None)
):
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
    
    user = register_user(
        email, 
        password, 
        nickname, 
        role="merchant", 
        shop_name=shop_name,
        business_category=business_category,
        business_license=license_data,
        id_card=id_card_data,
        security_question=security_question,
        security_answer=security_answer
    )
    return {"code": 0, "data": user, "message": "注册成功，请等待管理员审核"}


@router.post("/login")
def c_login(req: LoginRequest):
    result = login_user(req.email, req.password)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/profile")
def c_get_profile(user: dict = Depends(get_current_user)):
    profile = get_user_profile(user["user_id"])
    return {"code": 0, "data": profile, "message": "success"}


@router.post("/refresh-token")
def c_refresh_token(user: dict = Depends(get_current_user)):
    """用当前token重新生成新token（从数据库取最新role等信息）"""
    result = refresh_token(user["user_id"])
    return {"code": 0, "data": result, "message": "success"}


@router.put("/address")
def c_update_address(req: UpdateAddressRequest, user: dict = Depends(get_current_user)):
    result = update_user_address(user["user_id"], req.address)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/profile")
def c_update_profile(req: UpdateNicknameRequest, user: dict = Depends(get_current_user)):
    result = update_user_nickname(user["user_id"], req.nickname)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/password")
def c_change_password(req: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    result = change_password(user["user_id"], req.old_password, req.new_password)
    return {"code": 0, "data": result, "message": "success"}


@router.put("/shop")
def c_update_shop(req: UpdateShopInfoRequest, user: dict = Depends(get_current_user)):
    result = update_shop_info(user["user_id"], req.shop_name, req.shop_description, req.shop_logo)
    return {"code": 0, "data": result, "message": "success"}


@router.post("/avatar")
async def c_upload_avatar(avatar: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """上传头像：接收图片文件，转为 base64 data URL 存入数据库"""
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if avatar.content_type not in allowed_types:
        raise ValidationError("仅支持 jpg/png/gif/webp 格式图片")

    max_size = 2 * 1024 * 1024  # 2 MB
    content = await avatar.read()
    if len(content) > max_size:
        raise ValidationError("图片大小不能超过 2MB")

    ext_map = {
        "image/jpeg": "jpeg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
    }
    mime = avatar.content_type
    ext = ext_map.get(mime, "jpeg")
    b64 = base64.b64encode(content).decode("utf-8")
    data_url = f"data:{mime};base64,{b64}"

    result = update_avatar(user["user_id"], data_url)
    return {"code": 0, "data": result, "message": "头像上传成功"}


@router.post("/email-change/apply")
def c_apply_email_change(req: EmailChangeApplyRequest, user: dict = Depends(get_current_user)):
    """用户提交换绑邮箱申请"""
    result = apply_email_change(user["user_id"], req.new_email)
    return {"code": 0, "data": result, "message": "申请已提交，请等待管理员审核"}


@router.post("/forgot-password/question")
def c_get_security_question(req: GetSecurityQuestionRequest):
    """根据邮箱获取安全问题"""
    result = get_security_question(req.email)
    return {"code": 0, "data": result, "message": "success"}


@router.post("/forgot-password/verify")
def c_verify_security_answer(req: VerifySecurityAnswerRequest):
    """验证安全问题答案"""
    result = verify_security_answer(req.email, req.answer)
    return {"code": 0, "data": result, "message": "答案正确"}


@router.post("/forgot-password/reset")
def c_reset_password_by_answer(req: ResetPasswordByAnswerRequest):
    """通过安全问题答案重置密码"""
    result = reset_password_by_answer(req.email, req.answer, req.new_password)
    return {"code": 0, "data": result, "message": "密码重置成功"}
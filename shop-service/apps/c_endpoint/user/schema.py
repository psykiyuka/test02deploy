from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    email: str
    password: str
    nickname: str
    security_question: str = "我最喜欢的食物"
    security_answer: str = "番茄炒蛋"

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 6:
            raise ValueError("密码长度不能少于6位")
        return v.strip()

    @field_validator("security_question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("安全问题不能为空")
        return v.strip()

    @field_validator("security_answer")
    @classmethod
    def answer_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("安全问题答案不能为空")
        return v.strip()


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("邮箱不能为空")
        return v.strip()


class UpdateAddressRequest(BaseModel):
    address: str

    @field_validator("address")
    @classmethod
    def address_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("收货地址不能为空")
        return v.strip()


class MerchantRegisterRequest(BaseModel):
    email: str
    password: str
    nickname: str
    shop_name: str
    business_category: str | None = None
    business_license: str | None = None
    id_card: str | None = None

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 8:
            raise ValueError("密码长度不能少于8位")
        return v.strip()

    @field_validator("shop_name")
    @classmethod
    def shop_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("店铺名称不能为空")
        return v.strip()


class UpdateShopInfoRequest(BaseModel):
    shop_name: str
    shop_description: str | None = None
    shop_logo: str | None = None

    @field_validator("shop_name")
    @classmethod
    def shop_name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("店铺名称不能为空")
        return v.strip()


class UpdateNicknameRequest(BaseModel):
    nickname: str

    @field_validator("nickname")
    @classmethod
    def nickname_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("昵称不能为空")
        if len(v.strip()) > 50:
            raise ValueError("昵称长度不能超过50个字符")
        return v.strip()


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password")
    @classmethod
    def old_password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("原密码不能为空")
        return v.strip()

    @field_validator("new_password")
    @classmethod
    def new_password_valid(cls, v: str) -> str:
        if not v or len(v.strip()) < 8:
            raise ValueError("新密码长度不能少于8位")
        return v.strip()


class EmailChangeApplyRequest(BaseModel):
    new_email: str

    @field_validator("new_email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if not v or "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.strip()


class GetSecurityQuestionRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if not v or "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.strip()


class VerifySecurityAnswerRequest(BaseModel):
    email: str
    answer: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if not v or "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.strip()

    @field_validator("answer")
    @classmethod
    def answer_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("安全问题答案不能为空")
        return v.strip()


class ResetPasswordByAnswerRequest(BaseModel):
    email: str
    answer: str
    new_password: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if not v or "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.strip()

    @field_validator("answer")
    @classmethod
    def answer_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("安全问题答案不能为空")
        return v.strip()

    @field_validator("new_password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if not v or len(v.strip()) < 8:
            raise ValueError("密码长度不能少于8位")
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含字母和数字")
        return v.strip()
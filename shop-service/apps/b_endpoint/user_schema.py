from pydantic import BaseModel, field_validator


class ResetPasswordRequest(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 8:
            raise ValueError("密码长度不能少于8位")
        return v.strip()


class RejectMerchantRequest(BaseModel):
    reason: str | None = None
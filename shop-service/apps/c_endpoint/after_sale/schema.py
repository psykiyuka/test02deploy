from pydantic import BaseModel, field_validator


class CreateAfterSaleRequest(BaseModel):
    order_id: int
    type: str
    reason: str = ""

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        if v not in ("refund", "return", "exchange"):
            raise ValueError("售后类型无效，应为 refund/return/exchange")
        return v


class SubmitReturnLogisticsRequest(BaseModel):
    tracking_number: str
    carrier: str = "SF-Express"

    @field_validator("tracking_number")
    @classmethod
    def tracking_valid(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("快递单号不能为空")
        return v.strip()

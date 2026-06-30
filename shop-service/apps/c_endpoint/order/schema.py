from pydantic import BaseModel, field_validator
from typing import Optional, List


class CreateOrderRequest(BaseModel):
    address: str
    product_ids: Optional[List[int]] = None  # 仅结算选中的商品，None 表示全部

    @field_validator("address")
    @classmethod
    def address_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("收货地址不能为空")
        return v.strip()


class DirectBuyRequest(BaseModel):
    product_id: int
    quantity: int = 1
    address: str

    @field_validator("address")
    @classmethod
    def address_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("收货地址不能为空")
        return v.strip()

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("购买数量不能小于1")
        return v

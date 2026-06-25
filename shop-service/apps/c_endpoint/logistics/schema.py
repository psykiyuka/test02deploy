from typing import Optional
from pydantic import BaseModel, field_validator


class UpdateLogisticsRequest(BaseModel):
    status: str
    tracking_number: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        # 正向物流不含 returned（returned 仅售后退货场景使用）
        valid_statuses = ["pending", "picked_up", "in_transit", "out_for_delivery", "delivered"]
        if v not in valid_statuses:
            raise ValueError(f"状态必须是 {', '.join(valid_statuses)} 之一")
        return v
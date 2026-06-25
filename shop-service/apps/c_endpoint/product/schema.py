from pydantic import BaseModel, field_validator


class CreateProductRequest(BaseModel):
    name: str
    description: str = ""
    price: float
    image_url: str = ""
    stock: int = 0
    category_id: int

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("商品名称不能为空")
        return v.strip()

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("价格必须大于0")
        return v

    @field_validator("stock")
    @classmethod
    def stock_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("库存不能为负数")
        return v


class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    image_url: str | None = None
    stock: int | None = None
    category_id: int | None = None


class ToggleStatusRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in ("on_sale", "off_sale"):
            raise ValueError("状态值无效，应为 on_sale 或 off_sale")
        return v
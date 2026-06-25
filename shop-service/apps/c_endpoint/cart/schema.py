from pydantic import BaseModel, field_validator


class AddCartRequest(BaseModel):
    product_id: int
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("数量必须大于0")
        return v


class UpdateCartRequest(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("数量必须大于0")
        return v
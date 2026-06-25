from pydantic import BaseModel


class CreateAddressRequest(BaseModel):
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool = False


class UpdateAddressRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    detail: str | None = None
    is_default: bool | None = None

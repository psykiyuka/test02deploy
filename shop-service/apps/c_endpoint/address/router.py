from fastapi import APIRouter, Depends

from apps.common.auth import get_current_user
from domain.user_address import get_addresses, add_address, update_address, delete_address, set_default_address
from .schema import CreateAddressRequest, UpdateAddressRequest

router = APIRouter(prefix="/c-endpoint/addresses", tags=["C端-地址簿"])


@router.get("")
def c_get_addresses(user: dict = Depends(get_current_user)):
    addresses = get_addresses(user["user_id"])
    return {"code": 0, "data": addresses, "message": "success"}


@router.post("")
def c_add_address(req: CreateAddressRequest, user: dict = Depends(get_current_user)):
    result = add_address(
        user["user_id"], req.name, req.phone, req.province, req.city,
        req.district, req.detail, req.is_default,
    )
    return {"code": 0, "data": result, "message": "添加成功"}


@router.put("/{address_id}")
def c_update_address(address_id: int, req: UpdateAddressRequest, user: dict = Depends(get_current_user)):
    result = update_address(
        address_id, user["user_id"],
        name=req.name, phone=req.phone, province=req.province, city=req.city,
        district=req.district, detail=req.detail, is_default=req.is_default,
    )
    return {"code": 0, "data": result, "message": "更新成功"}


@router.delete("/{address_id}")
def c_delete_address(address_id: int, user: dict = Depends(get_current_user)):
    result = delete_address(address_id, user["user_id"])
    return {"code": 0, "data": result, "message": "删除成功"}


@router.put("/{address_id}/default")
def c_set_default_address(address_id: int, user: dict = Depends(get_current_user)):
    result = set_default_address(address_id, user["user_id"])
    return {"code": 0, "data": result, "message": "设置成功"}

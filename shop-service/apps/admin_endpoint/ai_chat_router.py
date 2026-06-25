"""
Admin 端 AI 客服知识库路由
Admin 可以上传系统级 FAQ（所有商家共享）
"""
from fastapi import APIRouter, Depends, Form, UploadFile, File
from typing import Optional

from apps.common.auth import get_current_admin
from domain.ai_chat.ai_chat_service import (
    create_kb_file,
    get_kb_files,
    delete_kb_file,
)

router = APIRouter(prefix="/admin-endpoint", tags=["Admin-AI客服"])


@router.post("/ai-kb/upload")
async def admin_upload_kb_file(
    file: UploadFile = File(...),
    product_id: Optional[int] = Form(None),
    user: dict = Depends(get_current_admin),
):
    """
    Admin 上传系统级 FAQ 文件（所有商家共享）
    文件格式：**问题** + 回答
    product_id: 可选，绑定到特定商品
    """
    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content = content_bytes.decode("gbk", errors="replace")

    file_type = "md"
    if "." in file.filename:
        ext = file.filename.split(".")[-1].lower()
        if ext in ("md", "txt", "markdown"):
            file_type = ext

    result = create_kb_file(
        merchant_id=0,  # is_system=True 时会存为 NULL
        filename=file.filename,
        content=content,
        file_type=file_type,
        product_id=product_id,
        is_system=True,
    )
    return {"code": 0, "data": result, "message": "系统级 FAQ 上传成功"}


@router.get("/ai-kb/files")
def admin_get_kb_files(
    product_id: Optional[int] = None,
    user: dict = Depends(get_current_admin),
):
    """查看系统级知识库文件列表"""
    files = get_kb_files(merchant_id=None)  # merchant_id=None 查询系统级
    return {"code": 0, "data": {"items": files, "total": len(files)}, "message": "success"}


@router.delete("/ai-kb/files/{file_id}")
def admin_delete_kb_file(
    file_id: int,
    user: dict = Depends(get_current_admin),
):
    """删除系统级知识库文件"""
    delete_kb_file(file_id, merchant_id=None)
    return {"code": 0, "message": "删除成功"}

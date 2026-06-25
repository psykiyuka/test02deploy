from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from apps.common.auth import get_current_merchant
from domain.ai_chat import create_kb_file, get_kb_files, delete_kb_file

router = APIRouter(prefix="/m-endpoint", tags=["M端-AI客服"])


# ── 商家端：知识库管理 ──

class AIChatAskRequest(BaseModel):
    question: str
    rewrite: bool = False


class AIChatUploadRequest(BaseModel):
    product_id: Optional[int] = None


@router.post("/ai-kb/upload")
async def m_upload_kb_file(
    file: UploadFile = File(...),
    product_id: Optional[int] = Form(None),
    user: dict = Depends(get_current_merchant),
):
    """上传 FAQ 文件（支持 .md / .txt）
    product_id: 可选，绑定到指定商品；不传则为商家级 FAQ
    """
    filename = file.filename
    content = (await file.read()).decode("utf-8", errors="ignore")
    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    if file_type not in ("md", "txt", "markdown"):
        return {"code": 400, "message": "暂仅支持 .md / .txt 格式"}

    result = create_kb_file(user["user_id"], filename, content, file_type, product_id=product_id)
    return {"code": 0, "data": result, "message": "上传成功"}


@router.get("/ai-kb/files")
def m_get_kb_files(
    product_id: Optional[int] = Query(None, description="按商品ID过滤，不传则返回所有"),
    user: dict = Depends(get_current_merchant),
):
    """查看已上传的知识库文件列表，可按商品过滤"""
    files = get_kb_files(user["user_id"], product_id=product_id)
    return {"code": 0, "data": {"items": files, "total": len(files)}}


@router.delete("/ai-kb/files/{file_id}")
def m_delete_kb_file(file_id: int, user: dict = Depends(get_current_merchant)):
    """删除知识库文件"""
    delete_kb_file(file_id, user["user_id"])
    return {"code": 0, "message": "删除成功"}

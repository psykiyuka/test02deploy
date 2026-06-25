from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from apps.common.auth import get_current_admin
from domain.chat.chat_service import (
    send_message,
    get_session_messages,
    mark_messages_read,
    get_admin_sessions,
)


router = APIRouter(prefix="/admin-endpoint/chat", tags=["Admin端-人工客服"])


class ReplyRequest(BaseModel):
    session_id: int
    message: str


@router.get("/sessions")
def admin_get_sessions(admin=Depends(get_current_admin)):
    """获取系统级会话列表"""
    sessions = get_admin_sessions()
    return {"code": 0, "data": sessions}


@router.get("/messages")
def admin_get_messages(session_id: int, after_id: Optional[int] = None, admin=Depends(get_current_admin)):
    """获取会话消息"""
    try:
        messages = get_session_messages(session_id, after_id=after_id, reader_role="admin")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"code": 0, "data": messages}


@router.post("/reply")
def admin_reply(request: ReplyRequest, admin=Depends(get_current_admin)):
    """发送回复"""
    try:
        result = send_message(request.session_id, admin["user_id"], "admin", request.message)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"code": 0, "data": result}


@router.post("/mark-read")
def admin_mark_read(session_id: int, admin=Depends(get_current_admin)):
    """标记消息已读"""
    mark_messages_read(session_id, "admin")
    return {"code": 0, "message": "已标记已读"}

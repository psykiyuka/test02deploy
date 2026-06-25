from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from apps.common.auth import get_current_merchant
from domain.chat.chat_service import (
    send_message,
    get_session_messages,
    mark_messages_read,
    get_merchant_sessions,
)


router = APIRouter(prefix="/m-endpoint/chat", tags=["M端-人工客服"])


class ReplyRequest(BaseModel):
    session_id: int
    message: str


@router.get("/sessions")
def m_get_sessions(merchant=Depends(get_current_merchant)):
    """获取分配给我的会话列表"""
    sessions = get_merchant_sessions(merchant["user_id"])
    return {"code": 0, "data": sessions}


@router.get("/messages")
def m_get_messages(session_id: int, after_id: Optional[int] = None, merchant=Depends(get_current_merchant)):
    """获取会话消息"""
    try:
        messages = get_session_messages(session_id, after_id=after_id, reader_id=merchant["user_id"], reader_role="merchant")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"code": 0, "data": messages}


@router.post("/reply")
def m_reply(request: ReplyRequest, merchant=Depends(get_current_merchant)):
    """发送回复"""
    try:
        result = send_message(request.session_id, merchant["user_id"], "merchant", request.message)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"code": 0, "data": result}


@router.post("/mark-read")
def m_mark_read(session_id: int, merchant=Depends(get_current_merchant)):
    """标记消息已读"""
    mark_messages_read(session_id, "merchant")
    return {"code": 0, "message": "已标记已读"}

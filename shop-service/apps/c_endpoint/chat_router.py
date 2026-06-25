from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from apps.common.auth import get_current_user
from domain.chat.chat_service import (
    create_or_get_session,
    send_message,
    get_session_messages,
    mark_messages_read,
    get_buyer_sessions,
    close_session,
)


router = APIRouter(prefix="/c-endpoint/chat", tags=["C端-人工客服"])


class CreateSessionRequest(BaseModel):
    product_id: Optional[int] = None


class SendMessageRequest(BaseModel):
    session_id: int
    message: str


@router.post("/session")
def c_create_session(request: CreateSessionRequest, user=Depends(get_current_user)):
    """创建或获取聊天会话（自动路由到商家或管理员）"""
    result = create_or_get_session(user["user_id"], product_id=request.product_id)
    return {"code": 0, "data": result}


@router.post("/send")
def c_send_message(request: SendMessageRequest, user=Depends(get_current_user)):
    """发送消息"""
    try:
        result = send_message(request.session_id, user["user_id"], "buyer", request.message)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"code": 0, "data": result}


@router.get("/messages")
def c_get_messages(session_id: int, after_id: Optional[int] = None, user=Depends(get_current_user)):
    """获取会话消息（after_id 用于轮询新消息）"""
    try:
        messages = get_session_messages(session_id, after_id=after_id, reader_id=user["user_id"], reader_role="buyer")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"code": 0, "data": messages}


@router.get("/sessions")
def c_get_sessions(user=Depends(get_current_user)):
    """获取我的会话列表"""
    sessions = get_buyer_sessions(user["user_id"])
    return {"code": 0, "data": sessions}


@router.post("/mark-read")
def c_mark_read(session_id: int, user=Depends(get_current_user)):
    """标记消息已读"""
    mark_messages_read(session_id, "buyer")
    return {"code": 0, "message": "已标记已读"}


@router.post("/close")
def c_close_session(session_id: int, user=Depends(get_current_user)):
    """关闭会话"""
    try:
        close_session(session_id, user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"code": 0, "message": "会话已关闭"}

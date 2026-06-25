from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional

from apps.common.auth import get_current_user
from domain.ai_chat import search_kb_chunks
from infrastructure.qwen_client import chat, rewrite_question


router = APIRouter(prefix="/c-endpoint", tags=["C端-AI客服"])


class AIChatAskRequest(BaseModel):
    merchant_id: int
    product_id: Optional[int] = None
    question: str
    rewrite: bool = False


@router.post("/ai-chat/ask")
def c_ask_ai(request: AIChatAskRequest):
    """
    买家向 AI 客服提问
    1. 若 rewrite=True，先润色问题
    2. 向量搜索最相关的 FAQ 条目
    3. 拼装 prompt 调用千问生成回答
    """
    question = request.question.strip()
    if not question:
        return {"code": 400, "message": "问题不能为空"}

    # 1. 润色问题（可选）
    search_question = question
    rewritten = None
    if request.rewrite:
        try:
            rewritten = rewrite_question(question)
            search_question = rewritten
        except Exception as e:
            # 润色失败不影响主流程，用原问题继续
            pass

    # 2. 向量搜索（优先商品级 FAQ，再搜商家级）
    chunks = search_kb_chunks(request.merchant_id, search_question, product_id=request.product_id, top_k=3)

    if not chunks:
        return {
            "code": 0,
            "data": {
                "answer": "抱歉，我暂时没有找到相关信息，建议联系商家客服。",
                "sources": [],
                "rewritten": rewritten,
            },
        }

    # 3. 拼装 prompt，调用千问生成回答
    context = "\n\n".join(
        f"Q: {c['question']}\nA: {c['answer']}" for c in chunks
    )

    messages = [
        {
            "role": "system",
            "content": "你是电商平台的AI客服助手。请根据提供的参考资料回答用户问题。"
            "如果参考资料中没有相关内容，请回复\"抱歉，我暂时没有找到相关信息\"。"
            "回答要简洁、友好，不超过200字。",
        },
        {
            "role": "user",
            "content": f"参考资料：\n{context}\n\n用户问题：{question}",
        },
    ]

    answer = chat(messages)

    return {
        "code": 0,
        "data": {
            "answer": answer,
            "sources": [{"question": c["question"]} for c in chunks],
            "rewritten": rewritten,
        },
    }

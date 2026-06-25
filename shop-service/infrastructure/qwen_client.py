"""
千问 API 封装（OpenAI 兼容模式）
与 rag-service 保持完全一致的实现方式
"""
import os
import logging
from typing import List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("shop")

API_KEY = os.getenv("QWEN_API_KEY", "")
BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
EMBEDDING_MODEL = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v3")
CHAT_MODEL = os.getenv("QWEN_CHAT_MODEL", "qwen3-8b")

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    return _client


def get_embedding(text: str) -> List[float]:
    """
    将文本转换为向量（OpenAI 兼容格式）
    text-embedding-v3 限制：最大 2048 tokens，约 6000 字符（中文）
    超长文本会自动截断
    """
    if not API_KEY:
        raise RuntimeError("未配置 QWEN_API_KEY 环境变量")

    # 记录输入长度，便于排查问题
    if len(text) > 500:
        logger.warning(f"[Qwen] get_embedding 输入文本较长({len(text)}字符)，前100字符: {text[:100]}...")

    # 截断：text-embedding-v3 限制 2048 tokens
    # 中文 1 字符 ≈ 1.5~2 tokens，取保守值 1500 字符（约 2000 tokens）
    if len(text) > 1500:
        logger.warning(f"[Qwen] 嵌入文本过长({len(text)}字符)，截断至1500字符: {text[:50]}...")
        text = text[:1500]

    resp = _get_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return resp.data[0].embedding


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    批量将文本转换为向量（自动分批，每批最多10条）
    texts: 文本列表，每个文本不超过 1500 字符
    返回: [[向量1], [向量2], ...] 顺序与输入一致
    """
    if not API_KEY:
        raise RuntimeError("未配置 QWEN_API_KEY 环境变量")

    # 截断超长文本
    trimmed = []
    for t in texts:
        if len(t) > 1500:
            logger.warning(f"[Qwen] 嵌入文本过长({len(t)}字符)，截断至1500字符: {t[:50]}...")
            trimmed.append(t[:1500])
        else:
            trimmed.append(t)

    # Qwen text-embedding-v3 批量最多 10 条
    BATCH = 10
    all_embeddings: List[List[float]] = []
    for i in range(0, len(trimmed), BATCH):
        batch = trimmed[i:i + BATCH]
        resp = _get_client().embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        all_embeddings.extend([d.embedding for d in resp.data])

    return all_embeddings


def chat(messages: List[dict], temperature: float = 0.7) -> str:
    """
    调用千问对话 API（OpenAI 兼容格式）
    messages: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    """
    if not API_KEY:
        raise RuntimeError("未配置 QWEN_API_KEY 环境变量")

    resp = _get_client().chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=temperature,
        extra_body={"enable_thinking": False},  # qwen3 必须显式关闭 thinking
    )
    return resp.choices[0].message.content


def rewrite_question(question: str) -> str:
    """
    将买家含糊的问题改写为 AI 更易理解的标准问法
    """
    messages = [
        {
            "role": "system",
            "content": "你是一个电商客服助手。用户的输入可能表达含糊、口语化或有错别字。"
            "请将用户的问题改写为清晰、标准的客服问题表述，保留原意，不超过50字。"
            "只返回改写后的问题，不要加任何解释。",
        },
        {"role": "user", "content": question},
    ]
    return chat(messages, temperature=0.3)

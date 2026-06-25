"""
AI 客服知识库 service
负责文件解析、向量化、检索
支持商家级（product_id=NULL）和商品级（product_id=指定商品）FAQ
"""
import os
import logging
import re
from typing import List, Optional

logger = logging.getLogger("shop")

from infrastructure.database import get_cursor
from infrastructure.qwen_client import get_embedding, get_embeddings


def parse_faq_content(content: str) -> List[dict]:
    """
    解析 FAQ 格式的文本内容
    支持格式：**问题** + 正文（与 Doc1-X1智能门锁FAQ.md 相同格式）
    返回 [{"question": "...", "answer": "..."}, ...]

    实现：按行扫描，以 ** 开头的行为问题，后续行直到下一个问题为回答
    """
    chunks = []
    current_question = None
    current_answer_lines = []

    for line in content.splitlines():
        stripped = line.strip()
        # 检测问题行：**问题内容**
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            # 保存上一个 QA
            if current_question and current_answer_lines:
                answer = "\n".join(current_answer_lines).strip()
                if answer:
                    chunks.append({"question": current_question, "answer": answer})
            # 开始新的问题
            current_question = stripped[2:-2].strip()  # 去掉 **
            current_answer_lines = []
        else:
            if current_question is not None:
                current_answer_lines.append(line)

    # 保存最后一个 QA
    if current_question and current_answer_lines:
        answer = "\n".join(current_answer_lines).strip()
        if answer:
            chunks.append({"question": current_question, "answer": answer})

    logger.info(f"[AI Chat] 解析 FAQ 内容：得到 {len(chunks)} 个 QA 条目")
    return chunks


def create_kb_file(
    merchant_id: int,
    filename: str,
    content: str,
    file_type: str,
    product_id: Optional[int] = None,
    is_system: bool = False,
) -> dict:
    """上传知识库文件：解析 + 向量化 + 入库
    is_system=True 时，merchant_id 忽略，存为系统级 FAQ（merchant_id=NULL）
    """
    chunks = parse_faq_content(content)
    if not chunks:
        raise ValueError("文件中未识别到 FAQ 内容，请检查格式是否为 **问题** + 回答")

    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO shop.kb_files (merchant_id, filename, content, file_type, product_id) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (None if is_system else merchant_id, filename, content, file_type, product_id),
        )
        file_id = cur.fetchone()["id"]

        # 批量获取 embedding
        questions = [chunk["question"] for chunk in chunks]
        embeddings = get_embeddings(questions)

        for i, chunk in enumerate(chunks):
            cur.execute(
                "INSERT INTO shop.kb_chunks (file_id, merchant_id, question, answer, embedding, product_id) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (file_id, None if is_system else merchant_id, chunk["question"], chunk["answer"], embeddings[i], product_id),
            )

    scope = "系统级" if is_system else (f"商品#{product_id}" if product_id else "商家级")
    logger.info(f"[AI Chat] 知识库文件上传成功：file_id={file_id}, chunks={len(chunks)}, 范围={scope}")
    return {"file_id": file_id, "chunk_count": len(chunks), "product_id": product_id, "is_system": is_system}


def get_kb_files(merchant_id: int, product_id: Optional[int] = None) -> list:
    """查看知识库文件列表，可按 product_id 过滤
    merchant_id=None 时查询系统级 FAQ（merchant_id IS NULL）
    """
    with get_cursor() as cur:
        if merchant_id is None:
            # 查询系统级
            cur.execute(
                "SELECT id, filename, file_type, product_id, created_at, "
                "(SELECT COUNT(*) FROM shop.kb_chunks WHERE file_id = kb_files.id) AS chunk_count "
                "FROM shop.kb_files WHERE merchant_id IS NULL ORDER BY created_at DESC",
            )
        elif product_id is not None:
            cur.execute(
                "SELECT id, filename, file_type, product_id, created_at, "
                "(SELECT COUNT(*) FROM shop.kb_chunks WHERE file_id = kb_files.id) AS chunk_count "
                "FROM shop.kb_files WHERE merchant_id = %s AND product_id = %s ORDER BY created_at DESC",
                (merchant_id, product_id),
            )
        else:
            cur.execute(
                "SELECT id, filename, file_type, product_id, created_at, "
                "(SELECT COUNT(*) FROM shop.kb_chunks WHERE file_id = kb_files.id) AS chunk_count "
                "FROM shop.kb_files WHERE merchant_id = %s ORDER BY created_at DESC",
                (merchant_id,),
            )
        return [dict(r) for r in cur.fetchall()]


def delete_kb_file(file_id: int, merchant_id: Optional[int] = None) -> None:
    """删除知识库文件（chunks 会级联删除）
    merchant_id=None 时删除系统级文件
    """
    with get_cursor() as cur:
        if merchant_id is None:
            cur.execute(
                "DELETE FROM shop.kb_files WHERE id = %s AND merchant_id IS NULL",
                (file_id,),
            )
        else:
            cur.execute(
                "DELETE FROM shop.kb_files WHERE id = %s AND merchant_id = %s",
                (file_id, merchant_id),
            )
        if cur.rowcount == 0:
            raise ValueError("文件不存在或无权限删除")


def search_kb_chunks(merchant_id: int, query: str, product_id: Optional[int] = None, top_k: int = 3) -> List[dict]:
    """
    向量搜索最相关的 FAQ 条目
    检索优先级：
      1. 有 product_id 时：优先商品级，再商家级，再系统级
      2. 无 product_id 时：商家级 → 系统级

    实现：分别查询各优先级，按距离排序后合并，保证优先级高的结果排在前面
    """
    query_embedding = get_embedding(query)

    with get_cursor() as cur:
        if product_id is not None:
            # 商品详情页：先查商品级，再查商家级，再查系统级
            # 用 UNION ALL + 优先级字段，确保排序正确
            cur.execute(
                "SELECT question, answer, distance, priority FROM ("
                "  SELECT question, answer, embedding <=> %s::vector AS distance, 0 AS priority "
                "  FROM shop.kb_chunks "
                "  WHERE merchant_id = %s AND product_id = %s "
                "  ORDER BY embedding <=> %s::vector LIMIT %s"
                ") AS product_results "
                "UNION ALL "
                "SELECT question, answer, distance, priority FROM ("
                "  SELECT question, answer, embedding <=> %s::vector AS distance, 1 AS priority "
                "  FROM shop.kb_chunks "
                "  WHERE merchant_id = %s AND (product_id IS NULL) "
                "  ORDER BY embedding <=> %s::vector LIMIT %s"
                ") AS merchant_results "
                "UNION ALL "
                "SELECT question, answer, distance, priority FROM ("
                "  SELECT question, answer, embedding <=> %s::vector AS distance, 2 AS priority "
                "  FROM shop.kb_chunks "
                "  WHERE merchant_id IS NULL AND product_id IS NULL "
                "  ORDER BY embedding <=> %s::vector LIMIT %s"
                ") AS system_results "
                "ORDER BY priority, distance LIMIT %s",
                (query_embedding, merchant_id, product_id, query_embedding, top_k,
                 query_embedding, merchant_id, query_embedding, top_k,
                 query_embedding, query_embedding, top_k,
                 top_k),
            )
        else:
            # 首页/聊天页：商家级 → 系统级
            cur.execute(
                "SELECT question, answer, distance, priority FROM ("
                "  SELECT question, answer, embedding <=> %s::vector AS distance, 0 AS priority "
                "  FROM shop.kb_chunks "
                "  WHERE merchant_id = %s AND (product_id IS NULL) "
                "  ORDER BY embedding <=> %s::vector LIMIT %s"
                ") AS merchant_results "
                "UNION ALL "
                "SELECT question, answer, distance, priority FROM ("
                "  SELECT question, answer, embedding <=> %s::vector AS distance, 1 AS priority "
                "  FROM shop.kb_chunks "
                "  WHERE merchant_id IS NULL AND product_id IS NULL "
                "  ORDER BY embedding <=> %s::vector LIMIT %s"
                ") AS system_results "
                "ORDER BY priority, distance LIMIT %s",
                (query_embedding, merchant_id, query_embedding, top_k,
                 query_embedding, query_embedding, top_k,
                 top_k),
            )

        rows = [dict(r) for r in cur.fetchall()]
        return rows[:top_k]

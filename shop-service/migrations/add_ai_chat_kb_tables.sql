-- AI 客服知识库表
-- 商家上传的 FAQ 文件

CREATE TABLE IF NOT EXISTS shop.kb_files (
    id SERIAL PRIMARY KEY,
    merchant_id INTEGER NOT NULL REFERENCES shop.users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    content TEXT,
    file_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- FAQ 条目向量化存储
CREATE TABLE IF NOT EXISTS shop.kb_chunks (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES shop.kb_files(id) ON DELETE CASCADE,
    merchant_id INTEGER NOT NULL REFERENCES shop.users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding vector(1024),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 向量索引（IVFFlat，加速余弦相似度搜索）
CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding
    ON shop.kb_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- 按 merchant_id 过滤的索引
CREATE INDEX IF NOT EXISTS idx_kb_chunks_merchant
    ON shop.kb_chunks(merchant_id);

CREATE INDEX IF NOT EXISTS idx_kb_files_merchant
    ON shop.kb_files(merchant_id);

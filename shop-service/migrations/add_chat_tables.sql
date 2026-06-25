-- 人工客服聊天表
-- 聊天会话表
CREATE TABLE IF NOT EXISTS customer_service.chat_sessions (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL,
    merchant_id INTEGER,           -- 商品级客服时填入，NULL=系统级（管理员处理）
    product_id INTEGER,            -- 来自商品详情页时填入
    status VARCHAR(20) DEFAULT 'active',  -- active / closed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 聊天消息表
CREATE TABLE IF NOT EXISTS customer_service.chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES customer_service.chat_sessions(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL,    -- 发送者 user.id
    sender_role VARCHAR(20) NOT NULL,  -- buyer / merchant / admin
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_chat_sessions_buyer ON customer_service.chat_sessions(buyer_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_merchant ON customer_service.chat_sessions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON customer_service.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_unread ON customer_service.chat_messages(session_id, is_read) WHERE NOT is_read;

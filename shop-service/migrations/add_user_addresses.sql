-- 用户地址簿表
CREATE TABLE IF NOT EXISTS shop.user_addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES shop.users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,           -- 收件人
    phone VARCHAR(20) NOT NULL,           -- 手机号
    province VARCHAR(50) NOT NULL,        -- 省
    city VARCHAR(50) NOT NULL,            -- 市
    district VARCHAR(50) NOT NULL,        -- 区
    detail VARCHAR(255) NOT NULL,         -- 详细地址
    is_default BOOLEAN DEFAULT FALSE,     -- 是否默认
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_addresses_user ON shop.user_addresses(user_id);

-- 商家入驻拒绝原因字段
ALTER TABLE shop.users ADD COLUMN IF NOT EXISTS reject_reason TEXT DEFAULT NULL;

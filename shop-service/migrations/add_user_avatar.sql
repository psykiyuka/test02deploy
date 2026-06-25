-- 给 users 表添加 avatar_url 字段
ALTER TABLE shop.users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500) DEFAULT NULL;

-- 商家入驻拒绝原因字段
ALTER TABLE shop.users ADD COLUMN IF NOT EXISTS reject_reason TEXT DEFAULT NULL;

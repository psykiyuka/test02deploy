-- 阶段一数据库迁移脚本
-- 修改时间: 2026-06-04
-- 修改内容:
-- 1. 用户表: 添加 merchant_status (商家审核状态)、shop_name (店铺名称)
-- 2. 商品表: 添加 merchant_id (商家ID)

-- =============================================
-- 1. 修改用户表 users
-- =============================================

-- 添加商家审核状态字段 (pending=待审核, approved=已通过, rejected=已拒绝)
ALTER TABLE shop.users ADD COLUMN IF NOT EXISTS merchant_status VARCHAR(20) DEFAULT NULL;

-- 添加店铺名称字段
ALTER TABLE shop.users ADD COLUMN IF NOT EXISTS shop_name VARCHAR(100) DEFAULT NULL;

-- 添加店铺描述字段
ALTER TABLE shop.users ADD COLUMN IF NOT EXISTS shop_description TEXT DEFAULT NULL;

-- 添加店铺Logo字段
ALTER TABLE shop.users ADD COLUMN IF NOT EXISTS shop_logo VARCHAR(500) DEFAULT NULL;

-- 更新现有管理员的merchant_status为approved（管理员不需要审核）
UPDATE shop.users SET merchant_status = 'approved' WHERE role = 'admin';

-- 为已存在的普通用户设置merchant_status为approved（普通买家不是商家，不需要审核）
UPDATE shop.users SET merchant_status = 'approved' WHERE role = 'user' AND merchant_status IS NULL;

-- =============================================
-- 2. 修改商品表 products
-- =============================================

-- 添加商家ID字段
ALTER TABLE shop.products ADD COLUMN IF NOT EXISTS merchant_id INTEGER DEFAULT NULL;

-- 添加商品审核状态字段 (pending=待审核, approved=已通过, rejected=已拒绝, on_sale=上架中, off_sale=已下架)
-- 注意：原有的status字段用于上下架状态，新字段用于审核状态
ALTER TABLE shop.products ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'approved';

-- 将现有商品设置为已审核（因为是旧数据）
UPDATE shop.products SET approval_status = 'approved', merchant_id = NULL WHERE approval_status = 'approved';

-- 添加商品描述字段（如果不存在）
ALTER TABLE shop.products ADD COLUMN IF NOT EXISTS description TEXT DEFAULT NULL;

-- 添加外键约束（可选，如果需要强关联）
-- ALTER TABLE shop.products ADD CONSTRAINT fk_merchant FOREIGN KEY (merchant_id) REFERENCES shop.users(id);

-- =============================================
-- 3. 创建索引优化查询性能
-- =============================================

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_merchant_status ON shop.users(merchant_status) WHERE merchant_status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_role ON shop.users(role);

-- 商品表索引
CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON shop.products(merchant_id) WHERE merchant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_approval_status ON shop.products(approval_status) WHERE approval_status IS NOT NULL;

-- =============================================
-- 4. 验证修改
-- =============================================

-- 查看用户表结构
-- SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'users' AND table_schema = 'shop';

-- 查看商品表结构
-- SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'products' AND table_schema = 'shop';

-- ============================================================
-- Phase 10: 数据库闭环重构
-- 1. orders 表添加 merchant_id，使订单直接关联商家
-- 2. 清理垃圾分类数据
-- 3. 将现有商品分配给商家
-- 4. 回填售后记录的 merchant_id
-- 5. 回填订单的 merchant_id
-- ============================================================

-- 1. orders 表添加 merchant_id
ALTER TABLE shop.orders ADD COLUMN IF NOT EXISTS merchant_id INTEGER;

-- 添加外键约束
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'orders_merchant_id_fkey'
        AND table_schema = 'shop' AND table_name = 'orders'
    ) THEN
        ALTER TABLE shop.orders
            ADD CONSTRAINT orders_merchant_id_fkey
            FOREIGN KEY (merchant_id) REFERENCES shop.users(id);
    END IF;
END $$;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_orders_merchant_id ON shop.orders(merchant_id) WHERE merchant_id IS NOT NULL;

-- 2. 清理垃圾分类数据（TestCategory, 123, abc 以及子分类）
DELETE FROM shop.categories WHERE id IN (10, 14, 16, 30);
-- 注意：如果有商品引用了这些分类，先移到合适的分类
UPDATE shop.products SET category_id = 1 WHERE category_id IN (10, 14, 16, 30);

-- 3. 将现有商品分配给商家（按分类分配给 merchant_id=13 的"数码精品店"）
-- 先确认有商家存在
DO $$
DECLARE
    merchant_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO merchant_count FROM shop.users WHERE role = 'merchant' AND merchant_status = 'approved';
    IF merchant_count = 0 THEN
        RAISE NOTICE '没有已审核的商家，跳过商品分配';
    END IF;
END $$;

-- 将所有 merchant_id 为 NULL 的商品分配给"数码精品店"（id=13）
UPDATE shop.products SET merchant_id = 13 WHERE merchant_id IS NULL;

-- 4. 回填售后记录的 merchant_id（从订单关联商品获取）
UPDATE shop.after_sale_requests a
SET merchant_id = p.merchant_id
FROM shop.order_items oi
JOIN shop.products p ON oi.product_id = p.id
WHERE a.order_id = oi.order_id
  AND a.merchant_id IS NULL
  AND p.merchant_id IS NOT NULL;

-- 5. 回填订单的 merchant_id（从订单项关联商品获取）
-- 注意：一个订单可能包含多个商家的商品，这里取第一个商品的商家
UPDATE shop.orders o
SET merchant_id = sub.merchant_id
FROM (
    SELECT DISTINCT ON (oi.order_id) oi.order_id, p.merchant_id
    FROM shop.order_items oi
    JOIN shop.products p ON oi.product_id = p.id
    WHERE p.merchant_id IS NOT NULL
    ORDER BY oi.order_id, oi.id
) sub
WHERE o.id = sub.order_id
  AND o.merchant_id IS NULL;

-- 6. 确保 products 的 merchant_id 不为 NULL（设置 NOT NULL 约束）
-- 先检查是否所有商品都有 merchant_id
-- ALTER TABLE shop.products ALTER COLUMN merchant_id SET NOT NULL;
-- 注意：暂时不加 NOT NULL 约束，因为管理员也可能直接创建商品

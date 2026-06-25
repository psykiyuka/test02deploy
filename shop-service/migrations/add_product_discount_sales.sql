-- ============================================================
-- 给 products 表添加 discount（折扣）和 sales（销量）字段
-- ============================================================

ALTER TABLE shop.products ADD COLUMN IF NOT EXISTS discount INTEGER DEFAULT NULL;
ALTER TABLE shop.products ADD COLUMN IF NOT EXISTS sales   INTEGER DEFAULT 0;

-- 索引加速销量排序
CREATE INDEX IF NOT EXISTS idx_products_sales ON shop.products(sales DESC) WHERE status = 'on_sale';

-- 为已有商品设置一些模拟销量数据
UPDATE shop.products SET sales = floor(random() * 5000 + 100)::int WHERE sales = 0 OR sales IS NULL;

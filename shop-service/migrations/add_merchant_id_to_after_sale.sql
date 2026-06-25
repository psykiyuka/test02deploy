-- 售后表添加 merchant_id 字段，实现商家隔离
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS merchant_id INTEGER REFERENCES shop.users(id);

-- 为已有售后记录回填 merchant_id（从订单关联的商品推断商家）
UPDATE shop.after_sale_requests ar
SET merchant_id = sub.merchant_id
FROM (
    SELECT DISTINCT ar2.id, p.merchant_id
    FROM shop.after_sale_requests ar2
    JOIN shop.order_items oi ON ar2.order_id = oi.order_id
    JOIN shop.products p ON oi.product_id = p.id
    WHERE ar2.merchant_id IS NULL
) sub
WHERE ar.id = sub.id;

CREATE INDEX IF NOT EXISTS idx_after_sale_merchant ON shop.after_sale_requests(merchant_id);

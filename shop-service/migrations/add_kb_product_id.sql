-- AI 客服知识库：支持商品级 FAQ
-- 给 kb_files 和 kb_chunks 加 product_id 字段
-- product_id 为 NULL 表示商家级（兜底），有值表示商品级

ALTER TABLE shop.kb_files
  ADD COLUMN IF NOT EXISTS product_id INTEGER REFERENCES shop.products(id) ON DELETE CASCADE;

ALTER TABLE shop.kb_chunks
  ADD COLUMN IF NOT EXISTS product_id INTEGER REFERENCES shop.products(id) ON DELETE CASCADE;

-- 索引：加速按 product_id 过滤
CREATE INDEX IF NOT EXISTS idx_kb_chunks_product
  ON shop.kb_chunks(product_id);

CREATE INDEX IF NOT EXISTS idx_kb_files_product
  ON shop.kb_files(product_id);

-- 更新检索索引（包含 product_id 条件）
-- 先删旧索引再重建（如果需要）
DROP INDEX IF EXISTS idx_kb_chunks_merchant;
CREATE INDEX IF NOT EXISTS idx_kb_chunks_merchant_product
  ON shop.kb_chunks(merchant_id, product_id);

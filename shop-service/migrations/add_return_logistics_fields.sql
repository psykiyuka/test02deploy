-- 售后表扩展退货物流字段
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS return_tracking_number VARCHAR(100);
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS return_carrier VARCHAR(50) DEFAULT 'SF-Express';
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS return_status VARCHAR(30) DEFAULT NULL;
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS returned_at TIMESTAMPTZ;
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS received_at TIMESTAMPTZ;
ALTER TABLE shop.after_sale_requests ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

COMMENT ON COLUMN shop.after_sale_requests.return_tracking_number IS '退货快递单号';
COMMENT ON COLUMN shop.after_sale_requests.return_carrier IS '退货快递公司';
COMMENT ON COLUMN shop.after_sale_requests.return_status IS '退货物流状态: pending_return/returned/received';
COMMENT ON COLUMN shop.after_sale_requests.approved_at IS '商家同意时间';
COMMENT ON COLUMN shop.after_sale_requests.returned_at IS '用户提交退货物流时间';
COMMENT ON COLUMN shop.after_sale_requests.received_at IS '商家确认收货时间';
COMMENT ON COLUMN shop.after_sale_requests.completed_at IS '售后完成时间';

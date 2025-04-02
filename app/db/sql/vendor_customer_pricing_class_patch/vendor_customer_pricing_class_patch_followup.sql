UPDATE vendor_pricing_by_customer
SET pricing_class_id = :new_pricing_class_id
WHERE id in :affected_ids
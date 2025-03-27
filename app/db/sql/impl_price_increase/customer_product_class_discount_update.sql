UPDATE vendor_product_class_discounts
SET discount = future.discount, effective_date = future.effective_date
FROM vendor_product_class_discounts_future as future
WHERE future.discount_id = vendor_product_class_discounts.id
    AND future.effective_date::DATE <= :today_date
    AND vendor_product_class_discounts.deleted_at IS NULL;

DELETE FROM vendor_product_class_discounts_future 
WHERE effective_date::DATE <= :today_date;
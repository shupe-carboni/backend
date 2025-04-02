SELECT 
    class.name AS mat_grp,
    discount,
    effective_date,
    vendor_customer_id AS customer_id
FROM vendor_product_class_discounts a
JOIN vendor_product_classes AS class
    ON class.id = product_class_id
WHERE vendor_customer_id = :customer_id
    AND a.effective_date <= CURRENT_DATE
    AND a.deleted_at IS NULL;
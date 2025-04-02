SELECT 
    class.name AS mat_grp,
    COALESCE(future.discount, a.discount, 0) as discount,
    COALESCE(future.effective_date, a.effective_date) as effective_date,
    vendor_customer_id AS customer_id
FROM vendor_product_class_discounts a
JOIN vendor_product_classes AS class
    ON class.id = product_class_id
LEFT JOIN vendor_product_class_discounts_future future
    ON a.id = future.discount_id
WHERE vendor_customer_id = :customer_id;
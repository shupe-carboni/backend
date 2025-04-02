SELECT 
    vp.vendor_product_identifier AS model,
    vendor_customer_id AS customer_id,
    COALESCE(future.discount, a.discount, 0) as discount,
    COALESCE(future.effective_date, a.effective_date) as effective_date
FROM vendor_product_discounts AS a
JOIN vendor_products AS vp
    ON vp.id = a.product_id
LEFT JOIN vendor_product_discounts_future AS future 
    ON a.id = future.discount_id
WHERE vendor_customer_id = :customer_id;
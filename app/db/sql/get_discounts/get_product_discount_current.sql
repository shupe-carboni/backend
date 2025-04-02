SELECT
    vp.vendor_product_identifier AS model,
    vendor_customer_id AS customer_id,
    discount
FROM vendor_product_discounts AS a
JOIN vendor_products AS vp 
    ON vp.id = a.product_id
WHERE vendor_customer_id = :customer_id
    AND a.effective_date <= CURRENT_DATE
    AND a.deleted_at is null;
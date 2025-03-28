SELECT (1-discount) as multiplier, effective_date
FROM vendor_product_discounts a
WHERE EXISTS (
    SELECT 1
    FROM vendor_customers b
    WHERE a.vendor_customer_id = b.id
    AND b.vendor_id = 'glasfloss'
)
AND EXISTS (
    SELECT 1
    FROM vendor_products c
    WHERE c.vendor_product_identifier = :model_number
    AND c.vendor_id = 'glasfloss'
    AND c.id = a.product_id
)
AND a.vendor_customer_id = :customer_id;
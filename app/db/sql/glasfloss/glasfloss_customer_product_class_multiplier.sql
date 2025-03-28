SELECT (1-discount) as multiplier, effective_date
FROM vendor_product_class_discounts a
WHERE EXISTS (
    SELECT 1
    FROM vendor_customers b
    WHERE a.vendor_customer_id = b.id
    AND b.vendor_id = 'glasfloss'
)
AND EXISTS (
    SELECT 1
    FROM vendor_product_classes c
    WHERE c.rank = 3
    AND c.name = :rank_3_name
    AND c.vendor_id = 'glasfloss'
    AND c.id = a.product_class_id
)
AND a.vendor_customer_id = :customer_id;
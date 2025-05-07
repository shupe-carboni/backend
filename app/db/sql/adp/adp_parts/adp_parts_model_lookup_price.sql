SELECT 
    CASE :use_future WHEN true
        THEN COALESCE(future.price, a.price)
        ELSE a.price
        END as price,
    CASE :use_future WHEN true
        THEN COALESCE(future.effective_date, a.effective_date)
        ELSE a.effective_date
        END as effective_date
FROM vendor_pricing_by_class a
LEFT JOIN vendor_pricing_by_class_future future
    ON a.id = future.price_id
WHERE EXISTS (
    SELECT 1
    FROM vendor_products b
    WHERE b.id = product_id
    AND b.vendor_product_identifier = :part_number
    AND b.vendor_id = 'adp'
) AND EXISTS (
    SELECT 1
    FROM vendor_pricing_classes c
    WHERE c.id = pricing_class_id
    AND c.name = :pricing_class_name
    AND c.vendor_id = 'adp'
);
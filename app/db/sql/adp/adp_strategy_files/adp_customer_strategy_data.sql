SELECT 
    vpbc.id as price_id,
    vpbc.product_id,
    vpbc.vendor_customer_id as customer_id, 
    classes.name as cat_1,
    vp.vendor_product_identifier as model_number,
    CASE :use_future
        WHEN true THEN COALESCE(vpbc_future.price, vpbc.price)
        ELSE vpbc.price
    END as price
FROM vendor_pricing_by_customer AS vpbc
JOIN vendor_products AS vp
    ON vp.id = vpbc.product_id
JOIN vendor_product_to_class_mapping AS mapping
    ON mapping.product_id = vp.id
JOIN vendor_product_classes AS classes
    ON classes.id = mapping.product_class_id
LEFT JOIN vendor_pricing_by_customer_future AS vpbc_future
    ON vpbc_future.price_id = vpbc.id
    AND vpbc_future.effective_date::date <= :ed
WHERE vpbc.vendor_customer_id = :customer_id
AND EXISTS (
    SELECT 1
    FROM vendor_pricing_classes AS vpc
    WHERE vpc.id = vpbc.pricing_class_id
    AND vpc.name = 'STRATEGY_PRICING'
    AND vp.vendor_id = 'adp'
)
AND classes.rank = 1
AND vpbc.deleted_at IS NULL;
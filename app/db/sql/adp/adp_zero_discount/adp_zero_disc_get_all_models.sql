SELECT vpbc.id, vp.vendor_product_identifier
FROM vendor_pricing_by_class vpbc
JOIN vendor_products vp
    ON vp.id = vpbc.product_id
    AND vp.vendor_id = 'adp'
JOIN vendor_pricing_classes price_classes
    ON price_classes.id = vpbc.pricing_class_id
    AND price_classes.vendor_id = 'adp'
WHERE price_classes.name = 'ZERO_DISCOUNT'
AND EXISTS (
    SELECT 1
    FROM vendor_product_to_class_mapping AS a
    JOIN vendor_product_classes as b
        ON a.product_class_id = b.id
    WHERE a.product_id = vp.id
        -- AND b.name in ('Air Handlers', 'Coils') 
        AND b.name in :product_categories
        AND b.rank = 1
);

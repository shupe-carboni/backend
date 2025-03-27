SELECT 
    vpbc.id,
    vp.vendor_product_identifier,
    vpbc.vendor_customer_id, 
    a.value AS private_label
FROM vendor_pricing_by_customer vpbc
JOIN vendor_products vp
    ON vp.id = vpbc.product_id
LEFT JOIN vendor_pricing_by_customer_attrs a
    ON a.pricing_by_customer_id = vpbc.id
    AND a.attr = 'private_label'
WHERE vp.vendor_id = 'adp'
    AND vpbc.deleted_at IS NULL
    AND vp.deleted_at IS NULL;
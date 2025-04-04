SELECT vc.id AS customer_id,
    vp.vendor_product_identifier AS part_number,
    vp.vendor_product_description AS description,
    vpa.value AS pkg_qty,
    vpbc.price::float / 100 as preferred,
    vpbc.price::float / 100 as standard
FROM vendor_customers vc
JOIN vendor_pricing_by_customer vpbc ON vpbc.vendor_customer_id = vc.id
JOIN vendor_products vp ON vp.id = vpbc.product_id
JOIN vendor_product_attrs vpa ON vpa.vendor_product_id = vp.id
LEFT JOIN vendor_pricing_by_customer_attrs vpca
    ON vpca.pricing_by_customer_id = vpbc.id and vpca.attr = 'sort_order'
WHERE vc.id = :customer_id
    AND vpa.attr = 'pkg_qty'
    AND EXISTS (
        SELECT 1
        FROM vendor_pricing_classes vpc
        WHERE vpc.id = vpbc.pricing_class_id
            AND vpc.name IN ('PREFERRED_PARTS','STANDARD_PARTS')
            AND vpc.vendor_id = 'adp'
    )
ORDER BY vpca.value::int;
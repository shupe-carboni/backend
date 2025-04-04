SELECT 
    pricing_by_customer_id as price_id,
    value as "category"
FROM vendor_pricing_by_customer_attrs
WHERE pricing_by_customer_id IN :ids
    AND attr = 'custom_description'
    AND EXISTS (
        SELECT 1
        FROM vendor_pricing_by_customer a
        JOIN vendor_customers b
            ON b.id = a.vendor_customer_id
        WHERE a.id = vendor_pricing_by_customer_attrs.pricing_by_customer_id
            AND b.vendor_id = 'adp'
    );
INSERT INTO vendor_pricing_by_class_future (
    price_id,
    price,
    effective_date
)
SELECT 
    class_price.id, 
    CAST(ROUND(price * :multiplier) AS INTEGER),
    :ed
FROM vendor_pricing_by_class AS class_price
WHERE EXISTS (
    SELECT 1
    FROM vendor_products
    WHERE vendor_products.id = class_price.product_id
    AND vendor_products.vendor_id = :vendor_id
) 
AND deleted_at IS NULL;
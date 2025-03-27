INSERT INTO vendor_pricing_by_customer_future (
    price_id,
    price,
    effective_date
)
SELECT 
    customer_price.id, 
    CAST(ROUND(price * :multiplier) AS INTEGER),
    :ed
FROM vendor_pricing_by_customer AS customer_price
WHERE EXISTS (
    SELECT 1
    FROM vendor_products
    WHERE vendor_products.id = customer_price.product_id
    AND vendor_products.vendor_id = :vendor_id
) 
AND deleted_at IS NULL;
INSERT INTO vendor_pricing_by_class_future (
    price_id,
    price,
    effective_date
)
SELECT
    class_price.id,
    (new.price * 100)::INT,
    :ed
FROM vendor_pricing_by_class AS class_price
JOIN vendor_products AS products
    ON products.id = class_price.product_id
JOIN class_price_temp AS new
    ON new.price_class_id = class_price.pricing_class_id
    AND new.model = products.vendor_product_identifier
WHERE products.vendor_id = 'friedrich';

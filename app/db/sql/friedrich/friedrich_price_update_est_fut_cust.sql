INSERT INTO vendor_pricing_by_customer_future (
    price_id,
    price,
    effective_date
)
SELECT
    customer_price.id,
    (new.price * 100)::INT,
    :ed
FROM vendor_pricing_by_customer AS customer_price
JOIN vendor_products AS products
    ON products.id = customer_price.product_id
JOIN customer_price_temp AS new
    ON new.customer_id = customer_price.vendor_customer_id
    AND new.model = products.vendor_product_identifier
WHERE products.vendor_id = 'friedrich';
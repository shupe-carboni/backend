INSERT INTO vendor_pricing_by_customer_future (
    price_id,
    price,
    effective_date
)
SELECT 
    customer_price.id,
    new.price,
    :ed
FROM vendor_pricing_by_customer AS customer_price
JOIN adp_customer_nets AS new
    ON new.id = customer_price.id;
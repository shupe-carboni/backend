UPDATE vendor_pricing_by_customer_future
SET effective_date = :new_eff_date
WHERE EXISTS (
    SELECT 1
    FROM vendor_pricing_by_customer customer_pricing
    JOIN vendor_products products
        ON products.id = customer_pricing.product_id
    WHERE products.vendor_id = :vendor_id
        AND customer_pricing.id = vendor_pricing_by_customer_future.price_id
)
AND effective_date = :curr_eff_date ;
UPDATE vendor_pricing_by_class_future
SET effective_date = :new_eff_date
WHERE EXISTS (
    SELECT 1
    FROM vendor_pricing_by_class class_pricing
    JOIN vendor_products products
        ON products.id = class_pricing.product_id
    WHERE products.vendor_id = :vendor_id
        AND class_pricing.id = vendor_pricing_by_class_future.price_id
)
AND effective_date = :curr_eff_date ;
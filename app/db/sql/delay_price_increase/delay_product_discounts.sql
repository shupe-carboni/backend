UPDATE vendor_product_discounts_future
SET effective_date = :new_eff_date
WHERE EXISTS (
    SELECT 1
    FROM vendor_product_discounts discounts
    JOIN vendor_products products
        ON products.id = discounts.product_id
    WHERE products.vendor_id = :vendor_id
        AND discounts.id = vendor_product_discounts_future.discount_id
)
AND effective_date = :curr_eff_date ;
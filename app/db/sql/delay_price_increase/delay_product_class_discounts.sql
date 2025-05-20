UPDATE vendor_product_class_discounts_future
SET effective_date = :new_eff_date
WHERE EXISTS (
    SELECT 1
    FROM vendor_product_class_discounts discounts
    JOIN vendor_product_classes product_classes
        ON product_classes.id = discounts.product_class_id
    WHERE product_classes.vendor_id = :vendor_id
        AND discounts.id = vendor_product_class_discounts_future.discount_id
)
AND effective_date = :curr_eff_date ;
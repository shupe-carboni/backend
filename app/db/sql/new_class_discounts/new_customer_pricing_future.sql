-- recalculate new future pricing
-- sig is used to determine where to round off
-- ex. sig == 100 means to round to the nearest dollar whereas sig == 1 rounds to cents
INSERT INTO vendor_pricing_by_customer_future (
    price_id,
    price,
    effective_date
)
SELECT 
    :new_price_class_id AS pricing_class_id,
    d.id AS product_id,
    f.id AS vendor_customer_id,
    true AS use_as_override,
    CASE
        WHEN a.discount < 1 THEN CAST((
            ROUND((e.price::float * (1-a.discount))/:sig)*:sig
        ) AS INT)
        ELSE CAST((
            ROUND((e.price::float * (1-a.discount/100))/:sig)*:sig
        ) AS INT)
    END as price,
    CURRENT_DATE as effective_date
FROM vendor_product_class_discounts AS a
-- map product class
JOIN vendor_product_classes AS b
    ON b.id = a.product_class_id
JOIN vendor_product_to_class_mapping AS c
    ON c.product_class_id = b.id
JOIN vendor_products AS d
    ON d.id = c.product_id
-- map pricing by class
JOIN vendor_pricing_by_class AS e
    ON e.product_id = d.id
-- map customer
JOIN vendor_customers AS f
    ON f.id = a.vendor_customer_id
WHERE e.pricing_class_id = :ref_pricing_class_id
    AND a.id = :product_class_discount_id
    AND e.deleted_at IS NULL
    AND d.deleted_at IS NULL
    AND NOT EXISTS (
        SELECT 1
        FROM vendor_pricing_by_customer_future ref_future
        WHERE ref_future.price_id = e.id
        AND ref_vpc.pricing_class_id = :new_price_class_id
    );
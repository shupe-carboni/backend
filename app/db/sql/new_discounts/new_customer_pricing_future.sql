-- recalculate new future pricing
-- sig is used to determine where to round off
-- ex. sig == 100 means to round to the nearest dollar
-- whereas sig == 1 rounds to cents
INSERT INTO vendor_pricing_by_customer_future (
    price_id,
    price,
    effective_date
)
SELECT 
    g.id,
    CASE
        WHEN a.discount < 1 THEN CAST((
            ROUND((future.price::float * (1-a.discount))/:sig)*:sig
        ) AS INT)
        ELSE CAST((
            ROUND((future.price::float * (1-a.discount/100))/:sig)*:sig
        ) AS INT)
    END as price,
    future.effective_date as effective_date
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
-- map future ref class price
JOIN vendor_pricing_by_class_future as future
    ON future.price_id = e.id
-- map customer
JOIN vendor_customers AS f
    ON f.id = a.vendor_customer_id
JOIN vendor_pricing_by_customer AS g 
    ON g.vendor_customer_id = f.id 
    AND g.product_id = d.id
WHERE e.pricing_class_id = :ref_pricing_class_id
    AND a.id = :product_class_discount_id
    AND e.deleted_at IS NULL
    AND d.deleted_at IS NULL
    AND :discount_type = "product_class"
    AND g.use_as_override
    AND NOT EXISTS (
        SELECT 1
        FROM vendor_pricing_by_customer_future ref_future
        WHERE ref_future.price_id = g.id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM vendor_product_discounts product_discounts
        WHERE product_discounts.product_id = d.id
        AND product_discounts.vendor_customer_id = f.id
    )

UNION ALL

SELECT 
    g.id,
    CASE
        WHEN a.discount < 1 THEN CAST((
            ROUND((future.price::float * (1-a.discount))/:sig)*:sig
        ) AS INT)
        ELSE CAST((
            ROUND((future.price::float * (1-a.discount/100))/:sig)*:sig
        ) AS INT)
    END as price,
    future.effective_date as effective_date
FROM vendor_product_discounts AS a
JOIN vendor_products AS d
    ON d.id = c.product_id
-- map pricing by class
JOIN vendor_pricing_by_class AS e
    ON e.product_id = d.id
-- map future ref class price
JOIN vendor_pricing_by_class_future as future
    ON future.price_id = e.id
-- map customer
JOIN vendor_customers AS f
    ON f.id = a.vendor_customer_id
JOIN vendor_pricing_by_customer AS g 
    ON g.vendor_customer_id = f.id 
    AND g.product_id = d.id
WHERE e.pricing_class_id = :ref_pricing_class_id
    AND a.id = :product_class_discount_id
    AND e.deleted_at IS NULL
    AND d.deleted_at IS NULL
    AND :discount_type = "product"
    AND g.use_as_override
    AND NOT EXISTS (
        SELECT 1
        FROM vendor_pricing_by_customer_future ref_future
        WHERE ref_future.price_id = g.id
    );
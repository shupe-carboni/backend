-- recalculate current pricing
-- sig is used to determine where to round off
-- ex. sig == 100 means to round to the nearest dollar whereas sig == 1 rounds to cents
UPDATE vendor_pricing_by_customer
SET
    price = new.calculated_price,
    effective_date = :effective_date
FROM (
    SELECT 
        g.id as price_by_customer_id,
        CASE
            WHEN product_class_discounts.discount < 1 THEN CAST((
                ROUND((e.price::float * (1-product_class_discounts.discount))/:sig)*:sig
            ) AS INT)
            ELSE CAST((
                ROUND((e.price::float * (1-product_class_discounts.discount/100))/:sig)*:sig
            ) AS INT)
        END as calculated_price
    FROM vendor_product_class_discounts AS product_class_discounts
        -- map product class
        JOIN vendor_product_classes AS b
            ON b.id = product_class_discounts.product_class_id
        JOIN vendor_product_to_class_mapping AS c
            ON c.product_class_id = b.id
        JOIN vendor_products AS d
            ON d.id = c.product_id
        -- map pricing by class
        JOIN vendor_pricing_by_class AS e
            ON e.product_id = d.id
        -- map customer
        JOIN vendor_customers AS f
            ON f.id = product_class_discounts.vendor_customer_id
        -- map pricing by customer
        JOIN vendor_pricing_by_customer AS g
            ON g.vendor_customer_id = f.id
            AND g.product_id = d.id
    WHERE e.pricing_class_id = :pricing_class_id
        AND product_class_discounts.id = :product_class_discount_id
    -- target only pricing that explicitly overrides the class-based version
        AND g.use_as_override
        AND g.deleted_at IS NULL
        AND :discount_type = 'product_class'

    UNION ALL

    SELECT 
        g.id as price_by_customer_id,
        CASE
            WHEN product_discounts.discount < 1 THEN CAST((
                ROUND((e.price::float * (1-product_discounts.discount))/:sig)*:sig
            ) AS INT)
            ELSE CAST((
                ROUND((e.price::float * (1-product_discounts.discount/100))/:sig)*:sig
            ) AS INT)
        END as calculated_price
        FROM vendor_product_discounts AS product_discounts
        JOIN vendor_products AS d
            ON d.id = product_discounts.product_id
        -- map pricing by class
        JOIN vendor_pricing_by_class AS e
            ON e.product_id = d.id
        -- map customer
        JOIN vendor_customers AS f
            ON f.id = product_discounts.vendor_customer_id
        -- map pricing by customer
        JOIN vendor_pricing_by_customer AS g
            ON g.vendor_customer_id = f.id
            AND g.product_id = d.id
    WHERE e.pricing_class_id = :pricing_class_id
        AND product_discounts.id = :product_class_discount_id
    -- target only pricing that explicitly overrides the class-based version
        AND g.use_as_override
        AND g.deleted_at IS NULL
        AND :discount_type = 'product'
) as new
WHERE new.price_by_customer_id = vendor_pricing_by_customer.id
AND deleted_at IS NULL;
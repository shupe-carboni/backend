-- get price ids affected by a patch to a customer class assignment
SELECT c.id
FROM vendor_customer_pricing_classes AS a
JOIN vendor_pricing_classes as b
    ON b.id = a.pricing_class_id
JOIN vendor_pricing_by_customer as c
    ON b.id = c.pricing_class_id
WHERE b.vendor_id = :vendor_id
    AND a.deleted_at is null
    AND c.use_as_override
    AND a.id = :affected_customer_pricing_class
    AND EXISTS (
        SELECT 1
        FROM vendor_customers
        WHERE vendor_customers.id = a.vendor_customer_id
        AND vendor_customers.id = c.vendor_customer_id
        AND vendor_customers.id = :customer_id
    );
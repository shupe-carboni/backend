SELECT 
    vendor_customers.id AS customer_id,
    vendor_customer_attrs.id as attr_id,
    attr,
    value,
    type  
FROM vendor_customers 
JOIN vendor_customer_attrs 
    ON vendor_customer_attrs.vendor_customer_id = vendor_customers.id
WHERE attr in ('ppf','terms')
    AND vendor_id = 'adp'
    AND vendor_customer_attrs.deleted_at IS NULL
    AND vendor_customers.deleted_at IS NULL
    AND vendor_customers.id = :customer_id;
SELECT DISTINCT
    vc.id as id, 
    vc.name AS adp_alias,
    customers.name as customer,
    customers.id as sca_id, 
    vca.value::bool as preferred_parts
FROM vendor_customers vc
JOIN customer_location_mapping clm ON clm.vendor_customer_id = vc.id
JOIN sca_customer_locations scl ON scl.id = clm.customer_location_id
JOIN sca_customers customers ON customers.id = scl.customer_id
JOIN vendor_customer_attrs vca ON vca.vendor_customer_id = vc.id
WHERE vc.vendor_id = 'adp'
    AND vca.attr = 'preferred_parts';
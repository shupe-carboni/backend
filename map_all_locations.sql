CREATE OR REPLACE FUNCTION add_all_customer_locations_to_mapping(
    vendor_customer_name TEXT,
    customer_name TEXT,
    vendor_name TEXT
)
RETURNS VOID AS $$
DECLARE
    selected_vendor_id VARCHAR;
    vendor_customer_id INT;
BEGIN
    -- Fetch the vendor ID
    SELECT id INTO selected_vendor_id
    FROM vendors
    WHERE id = vendor_name;

    IF selected_vendor_id IS NULL THEN
        RAISE EXCEPTION 'Vendor with name "%" does not exist.', vendor_name;
    END IF;

    -- Fetch the vendor_customer ID for the vendor
    SELECT id INTO vendor_customer_id
    FROM vendor_customers
    WHERE name = vendor_customer_name AND vendor_id = selected_vendor_id;

    IF vendor_customer_id IS NULL THEN
        RAISE EXCEPTION 'Vendor customer with name "%" for vendor "%" does not exist.', 
            vendor_customer_name, vendor_name;
    END IF;

    -- Insert all customer locations into the mapping table
    INSERT INTO customer_location_mapping (customer_location_id, vendor_customer_id)
    SELECT 
        cl.id AS customer_location_id,
        vendor_customer_id
    FROM 
        sca_customer_locations cl
    INNER JOIN sca_customers c ON cl.customer_id = c.id
    WHERE 
        c.name = customer_name;

    RAISE NOTICE 'All locations for customer "%" have been mapped to vendor customer "%" under vendor "%".',
        customer_name, vendor_customer_name, vendor_name;
END;
$$ LANGUAGE plpgsql;


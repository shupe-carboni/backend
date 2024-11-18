CREATE OR REPLACE FUNCTION add_customer_location_mapping(
    customer_name TEXT,
    vendor_customer_name TEXT,
    city_name TEXT,
    state_name TEXT,
    vendor_name TEXT
)
RETURNS VOID AS $$
DECLARE
    selected_customer_id INT;
    vendor_name_id VARCHAR;
    vendor_customer_id INT;
    customer_location_id INT;
    selected_place_id INT;
BEGIN
    -- Fetch the vendor ID
    SELECT id INTO vendor_name_id
    FROM vendors
    WHERE id = vendor_name;

    IF vendor_name_id IS NULL THEN
        RAISE EXCEPTION 'Vendor with name "%" does not exist.', vendor_name;
    END IF;

    -- Fetch the customer ID
    SELECT id INTO selected_customer_id
    FROM sca_customers
    WHERE name = customer_name;

    IF selected_customer_id IS NULL THEN
        RAISE EXCEPTION 'Customer with name "%" does not exist.', customer_name;
    END IF;

    -- Fetch the vendor customer ID specific to the vendor
    SELECT id INTO vendor_customer_id
    FROM vendor_customers
    WHERE name = vendor_customer_name AND vendor_customers.vendor_id = vendor_name_id;

    IF vendor_customer_id IS NULL THEN
        RAISE EXCEPTION 'Vendor customer with name "%" for vendor "%" does not exist.', vendor_customer_name, vendor_name;
    END IF;

    -- Fetch the place ID (city and state must match)
    SELECT id INTO selected_place_id
    FROM sca_places
    WHERE name = city_name
    AND state = state_name;

    IF selected_place_id IS NULL THEN
        RAISE EXCEPTION 'City "%" and State "%" do not exist in places table.', city_name, state_name;
    END IF;

    -- Fetch the customer location ID
    SELECT id INTO customer_location_id
    FROM sca_customer_locations
    WHERE customer_id = selected_customer_id AND place_id = selected_place_id;

    IF customer_location_id IS NULL THEN
        RAISE EXCEPTION 'Customer location for customer "%" in city "%" does not exist.', customer_name, city_name;
    END IF;

    -- Insert into customer_location_mapping
    INSERT INTO customer_location_mapping (customer_location_id, vendor_customer_id)
    VALUES (customer_location_id, vendor_customer_id);

    RAISE NOTICE 'Mapping added successfully for customer "%", vendor customer "%", city "%", and vendor "%".',
        customer_name, vendor_customer_name, city_name, vendor_name;
END;
$$ LANGUAGE plpgsql;


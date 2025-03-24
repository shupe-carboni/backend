BEGIN;
    -- add new product
    INSERT INTO vendor_products (vendor_id, vendor_product_identifier, vendor_product_description)
    SELECT DISTINCT 'atco', ap.part_number, ap.description
    FROM atco_pricing AS ap
    WHERE NOT EXISTS (
        SELECT 1
        FROM vendor_products
        WHERE vendor_products.vendor_product_identifier = ap.part_number
        AND vendor_products.vendor_id = 'atco'
    );

    -- associate any product to a product class where not associated
    INSERT INTO vendor_product_to_class_mapping(product_id, product_class_id)
    SELECT DISTINCT vp.id, vp_class.id
    FROM atco_pricing ap
    JOIN vendor_products vp
        ON vp.vendor_product_identifier = ap.part_number
        AND vp.vendor_id = 'atco'
    JOIN vendor_product_classes vp_class
        ON vp_class.name = ap.product_category_name
        AND vp_class.vendor_id = 'atco'
    WHERE NOT EXISTS (
        SELECT 1
        FROM vendor_products a
        JOIN vendor_product_to_class_mapping b
            ON b.product_id = a.id
            AND a.vendor_id = 'atco'
        WHERE a.vendor_product_identifier = ap.part_number
    );

    -- add new to LIST_PRICE
    INSERT INTO vendor_pricing_by_class (
        pricing_class_id,
        product_id,
        price,
        effective_date
    )
    SELECT (
        SELECT id 
        FROM vendor_product_classes
        WHERE vendor_id = 'atco' 
        AND name = 'LIST_PRICE') as pricing_class_id,
        vp.id as product_id,
        ap.price as price,
        CURRENT_TIMESTAMP as effective_date
    FROM atco_pricing AS ap
    JOIN vendor_products AS vp
        ON vp.vendor_product_identifier = ap.part_number
        AND vp.vendor_id = 'atco'
    WHERE vp.id not in (
        SELECT DISTINCT product_id
        FROM vendor_pricing_by_class
    );
    -- establish future LIST_PRICE
    INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
    SELECT class_price.id, ap.price, CAST(:ed AS TIMESTAMP)
    FROM vendor_pricing_by_class AS class_price
    JOIN vendor_products vp 
        ON vp.id = class_price.product_id
        AND vp.vendor_id = 'atco'
    JOIN vendor_pricing_classes vpc_class
        ON vpc_class.id = class_price.pricing_class_id
        AND vpc_class.name = 'LIST_PRICE'
        AND vpc_class.vendor_id = 'atco'
    JOIN atco_pricing ap
        ON vp.vendor_product_identifier = ap.part_number
        AND vp.vendor_id = 'atco';

    -- establish future class based pricing other than LIST_PRICE using multipliers
    INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
    SELECT class_price.id, reference.new_price, CAST(:ed AS TIMESTAMP)
    FROM vendor_pricing_by_class AS class_price
    JOIN (
        SELECT vendor_pricing_by_class.id AS id, list_mapped.new_price AS new_price
        FROM vendor_pricing_by_class
        JOIN (
            SELECT a.product_id, b.name, pricing_class_name, ((price::float)*multiplier)::int as new_price
            FROM vendor_pricing_by_class AS a
            JOIN vendor_pricing_classes AS b
                ON b.id = a.pricing_class_id
                AND b.vendor_id = 'atco'
            JOIN vendor_products AS c
                ON c.id = a.product_id
                AND c.vendor_id = 'atco'
            JOIN vendor_product_to_class_mapping d
                ON d.product_id = c.id
            JOIN vendor_product_classes e
                ON e.id = d.product_class_id
                AND e.vendor_id = 'atco'
            JOIN atco_multipliers
                ON e.name = atco_multipliers.product_class_name
                AND e.vendor_id = 'atco'
            WHERE b.name = 'LIST_PRICE') AS list_mapped
        ON list_mapped.product_id = vendor_pricing_by_class.product_id
        JOIN vendor_pricing_classes
            ON vendor_pricing_classes.id = vendor_pricing_by_class.pricing_class_id
            AND vendor_pricing_classes.vendor_id = 'atco'
            AND vendor_pricing_classes.name = list_mapped.pricing_class_name
    ) AS reference
    ON reference.id = class_price.id;
    
    -- establish future customer specific class based pricing
    -- using product class multipliers and list pricing

    INSERT INTO vendor_pricing_by_customer_future (price_id, price, effective_date)
    SELECT customer_price.id, reference.new_price, CAST(:ed AS TIMESTAMP)
    FROM vendor_pricing_by_customer as customer_price
    JOIN (
        SELECT g.id,((1-e.discount)*a.price)::int new_price
        FROM vendor_pricing_by_class a
        JOIN vendor_products b
            ON b.id = a.product_id
            AND b.vendor_id = 'atco'
        JOIN vendor_product_to_class_mapping c
            ON c.product_id = b.id
        JOIN vendor_product_classes d
            ON d.id = c.product_class_id
            AND d.vendor_id = 'atco'
        JOIN vendor_product_class_discounts e 
            ON e.product_class_id = d.id
        JOIN vendor_customers f
            ON f.id = e.vendor_customer_id
            AND f.vendor_id = 'atco'
        JOIN vendor_pricing_by_customer g
            ON g.vendor_customer_id = f.id
            AND g.product_id = b.id
        WHERE EXISTS (
            SELECT 1
            FROM vendor_pricing_classes h
            WHERE h.id = a.pricing_class_id
            AND h.name = 'LIST_PRICE'
        )
    ) AS reference
    ON customer_price.id = reference.id;

    -- cleanup
    DROP TABLE IF EXISTS atco_multipliers;
    DROP TABLE IF EXISTS atco_pricing;
COMMIT;
from app.admin.models import ADPProductSheet, ADPCustomerRefSheet, DBOps

SQL = {
    ADPProductSheet.PARTS: {
        DBOps.SETUP: """
            CREATE TEMPORARY TABLE adp_parts (
                part_number varchar,
                description varchar,
                pkg_qty int,
                preferred int,
                standard int 
            );
        """,
        DBOps.POPULATE_TEMP: """
            INSERT INTO adp_parts
            VALUES (:part_number, :description, :pkg_qty, :preferred, :standard)
        """,
        DBOps.ESTABLISH_FUTURE: """
            -- preferred
            INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
            SELECT vpc.id, preferred, :ed
            FROM adp_parts
            JOIN vendor_products AS vp
                ON vp.vendor_product_identifier = part_number
                AND vp.vendor_id = 'adp'
            JOIN vendor_pricing_by_class vpc
                ON vpc.product_id = vp.id
            WHERE EXISTS (
                SELECT 1
                FROM vendor_pricing_classes
                WHERE vendor_pricing_classes.id = vpc.pricing_class_id
                AND vendor_pricing_classes.vendor_id = 'adp'
                AND vendor_pricing_classes.name = 'PREFERRED_PARTS'
            );
            -- standard
            INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
            SELECT vpc.id, standard, :ed
            FROM adp_parts
            JOIN vendor_products AS vp
                ON vp.vendor_product_identifier = part_number
                AND vp.vendor_id = 'adp'
            JOIN vendor_pricing_by_class vpc
                ON vpc.product_id = vp.id
            WHERE EXISTS (
                SELECT 1
                FROM vendor_pricing_classes
                WHERE vendor_pricing_classes.id = vpc.pricing_class_id
                AND vendor_pricing_classes.vendor_id = 'adp'
                AND vendor_pricing_classes.name = 'STANDARD_PARTS'
            )
        """,
        DBOps.INSERT_NEW_PRODUCT: """
            INSERT INTO vendor_products (
                vendor_id,
                vendor_product_identifier,
                vendor_product_description
            )
            SELECT DISTINCT 'adp', part_number, description
            FROM adp_parts
            WHERE adp_parts.part_number NOT IN (
                SELECT DISTINCT vendor_product_identifier
                FROM vendor_products
                WHERE vendor_id = 'adp'
            )
            RETURNING id;
        """,
        DBOps.SETUP_ATTRS: """
            INSERT INTO vendor_product_attrs(vendor_product_id, attr, type, value)
            SELECT vp.id, 'pkg_qty', 'NUMBER', adp_parts.pkg_qty
            FROM adp_parts
            JOIN vendor_products as vp
                ON vp.vendor_product_identifier = adp_parts.part_number
                AND vp.vendor_id = 'adp'
            WHERE vp.id IN :new_part_ids
        """,
        # set the future price as the current price effective today
        DBOps.INSERT_NEW_PRODUCT_PRICING: """
            -- preferred
            INSERT INTO vendor_pricing_by_class (
                pricing_class_id,
                product_id, 
                price, 
                effective_date
            )
            SELECT (
                    SELECT id 
                    FROM vendor_pricing_classes 
                    WHERE vendor_id = 'adp' 
                    AND name = 'PREFERRED_PARTS'
                ), 
                vp.id, preferred, CURRENT_TIMESTAMP
            FROM adp_parts
            JOIN vendor_products AS vp
                ON vp.vendor_product_identifier = part_number
                AND vp.vendor_id = 'adp'
            WHERE vp.id in :new_part_ids
            AND preferred IS NOT NULL;
            -- standard
            INSERT INTO vendor_pricing_by_class (
                pricing_class_id,
                product_id, 
                price, 
                effective_date
            )
            SELECT (
                    SELECT id 
                    FROM vendor_pricing_classes 
                    WHERE vendor_id = 'adp' 
                    AND name = 'STANDARD_PARTS'
                ), 
                vp.id, standard, CURRENT_TIMESTAMP
            FROM adp_parts
            JOIN vendor_products AS vp
                ON vp.vendor_product_identifier = part_number
                AND vp.vendor_id = 'adp'
            WHERE vp.id in :new_part_ids
            AND standard IS NOT NULL;
        """,
        # Use when establishing the future as the current
        DBOps.UPDATE_CUSTOMER_PRICING: """
            UPDATE vendor_pricing_by_customer
            SET price = new.price, effective_date = new.effective_date
            FROM vendor_pricing_by_class AS new
            JOIN vendor_pricing_classes
                ON vendor_pricing_classes.id = new.pricing_class_id
                AND vendor_pricing_classes.vendor_id = 'adp'
                AND vendor_pricing_classes.name IN ('PREFERRED_PARTS', 'STANDARD_PARTS')
            JOIN vendor_customer_pricing_classes AS vc_price_class
                ON vc_price_class.pricing_class_id = vendor_pricing_classes.id
            JOIN vendor_customers
                ON vendor_customers.id = vc_price_class.vendor_customer_id
            WHERE vendor_customers.id = vendor_pricing_by_customer.vendor_customer_id
                AND vendor_pricing_classes.id = vendor_pricing_by_customer.pricing_class_id
                AND new.product_id = vendor_pricing_by_customer.product_id
        """,
    },
    ADPCustomerRefSheet.CUSTOMER_DISCOUNT: {
        DBOps.SETUP: """
            CREATE TEMPORARY TABLE adp_mgds (
                customer varchar,
                mg char(2),
                discount float);
        """,
        DBOps.POPULATE_TEMP: """
            INSERT INTO adp_mgds
            VALUES (:customer, :mg, :discount);
        """,
        DBOps.INSERT_NEW_DISCOUNTS: """
            INSERT INTO vendor_product_class_discounts (
                product_class_id, vendor_customer_id, 
                discount, effective_date)
            SELECT vp_class.id, vc.id, new.discount, CURRENT_TIMESTAMP
            FROM adp_mgds as new
            JOIN vendor_product_classes vp_class
                ON vp_class.name = new.mg
                AND vp_class.rank = 2
                AND vp_class.vendor_id = 'adp'
            JOIN vendor_customers vc
                ON vc.name = new.customer
                AND vc.vendor_id = 'adp'
            WHERE NOT EXISTS (
                SELECT 1 
                FROM vendor_product_class_discounts a
                WHERE a.vendor_customer_id = vc.id
                    AND a.product_class_id = vp_class.id
                )
            RETURNING *;
        """,
        DBOps.ESTABLISH_FUTURE: """
            INSERT INTO vendor_product_class_discounts_future (
                discount_id,
                discount,
                effective_date
            )
            SELECT vpc_discount.id, discount, :ed
            FROM adp_mgds
            JOIN vendor_product_classes vp_class
                ON vp_class.name = adp_mgds.mg
                AND vp_class.rank = 2
                AND vp_class.vendor_id = 'adp'
            JOIN vendor_customers vc
                ON vc.name = adp_mgds.customer
                AND vc.vendor_id = 'adp'
        """,
        DBOps.TEARDOWN: """
            DROP TABLE IF EXISTS adp_mgds;
        """,
    },
    "adp_customers": {
        DBOps.SETUP: """
            CREATE TEMPORARY TABLE adp_customers (customer varchar);
        """,
        DBOps.POPULATE_TEMP: """
            INSERT INTO adp_customers VALUES (:customer);
        """,
        DBOps.INSERT_NEW_CUSTOMERS: """
            INSERT INTO vendor_customers (vendor_id, name)
            SELECT 'adp' vendor_id, customer
            FROM adp_customers
            WHERE adp_customers.customer NOT IN (
                SELECT DISTINCT name
                FROM vendor_customers a
                WHERE vendor_id = 'adp'
            );
        """,
        DBOps.TEARDOWN: """
            DROP TABLE IF EXISTS adp_customers;
        """,
    },
    ADPCustomerRefSheet.SPECIAL_NET: {
        DBOps.SETUP: """
            DROP TABLE IF EXISTS adp_snps;
            CREATE TEMPORARY TABLE adp_snps (
                customer varchar,
                description varchar,
                price int
            );
        """,
        DBOps.POPULATE_TEMP: """
            INSERT INTO adp_snps
            VALUES (:customer, :description, :price);
        """,
        DBOps.INSERT_NEW_DISCOUNTS: """
            INSERT INTO vendor_product_discounts (
                product_id, 
                vendor_customer_id,
                discount,
                effective_date
            )
            SELECT vp.id, vc.id,
                (1-(new.price::float / class_price.price::float))*100, CURRENT_TIMESTAMP
            FROM adp_snps AS new
            JOIN vendor_customers vc
                ON vc.name = new.customer
                AND vc.vendor_id = 'adp'
            JOIN vendor_products vp
                ON vp.vendor_product_identifier = new.description
                AND vp.vendor_id = 'adp'
            JOIN vendor_pricing_by_class AS class_price
                ON class_price.product_id = vp.id
            WHERE NOT EXISTS (
                select 1
                from vendor_product_discounts z
                where z.product_id = vp.id
                and z.vendor_customer_id = vc.id
            );
        """,
        DBOps.ESTABLISH_FUTURE: """
            INSERT INTO vendor_product_discounts_future (
                discount_id,
                discount,
                effective_date
            )
            SELECT 
                class_price.id,
                (1-(new.price::float / class_price_future.price::float))*100, 
                :ed
            FROM adp_snps AS new
            JOIN vendor_customers vc
                ON vc.name = new.customer
                AND vc.vendor_id = 'adp'
            JOIN vendor_products vp
                ON vp.vendor_product_identifier = new.description
                AND vp.vendor_id = 'adp'
            JOIN vendor_pricing_by_class AS class_price
                ON class_price.product_id = vp.id
            JOIN vendor_pricing_by_class_future AS class_price_future
                ON class_price_future.price_id = class_price.id
                WHERE class_price_future.effective_date = :ed
        """,
        DBOps.TEARDOWN: """
            DROP TABLE IF EXISTS adp_snps;
        """,
    },
}

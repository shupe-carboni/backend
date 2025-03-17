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
        DBOps.UPDATE_EXISTING: """
            -- preferred
            UPDATE vendor_pricing_by_class
            SET price = new.preferred, effective_date = :ed
            FROM adp_parts as new
            JOIN vendor_products vp
                ON vp.vendor_product_identifier = new.part_number
                AND vp.vendor_id = 'adp'
            WHERE vp.id = vendor_pricing_by_class.product_id
            AND EXISTS (
                SELECT 1
                FROM vendor_pricing_classes a
                WHERE a.id = pricing_class_id
                AND a.name = 'PREFERRED_PARTS'
            );
            -- standard
            UPDATE vendor_pricing_by_class
            SET price = new.standard, effective_date = :ed
            FROM adp_parts as new
            JOIN vendor_products vp
                ON vp.vendor_product_identifier = new.part_number
                AND vp.vendor_id = 'adp'
            WHERE vp.id = vendor_pricing_by_class.product_id
            AND EXISTS (
                SELECT 1
                FROM vendor_pricing_classes a
                WHERE a.id = pricing_class_id
                AND a.name = 'STANDARD_PARTS'
            );
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
                vp.id, preferred, :ed
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
                vp.id, standard, :ed
            FROM adp_parts
            JOIN vendor_products AS vp
                ON vp.vendor_product_identifier = part_number
                AND vp.vendor_id = 'adp'
            WHERE vp.id in :new_part_ids
            AND standard IS NOT NULL;
        """,
        DBOps.UPDATE_CUSTOMER_PRICING: """
            UPDATE vendor_pricing_by_customer
            SET price = new.price, effective_date = :ed
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
    }
}

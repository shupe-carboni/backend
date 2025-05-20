-- return a boolean array to determine which tables are going to be updated
SELECT
    EXISTS (
        SELECT 1
        FROM vendor_pricing_by_class_future
        WHERE EXISTS (
            SELECT 1
            FROM vendor_pricing_by_class class_pricing
            JOIN vendor_products products
                ON products.id = class_pricing.product_id
            WHERE products.vendor_id = :vendor_id
                AND class_pricing.id = vendor_pricing_by_class_future.price_id
        )
        AND effective_date = :curr_eff_date
    ) as any_class_pricing_future,
    EXISTS (
        SELECT 1
        FROM vendor_pricing_by_customer_future
        WHERE EXISTS (
            SELECT 1
            FROM vendor_pricing_by_customer customer_pricing
            JOIN vendor_products products
                ON products.id = customer_pricing.product_id
            WHERE products.vendor_id = :vendor_id
                AND customer_pricing.id = vendor_pricing_by_customer_future.price_id
        )
        AND effective_date = :curr_eff_date
    ) as any_customer_pricing_future,
    EXISTS (
        SELECT 1
        FROM vendor_product_class_discounts_future
        WHERE EXISTS (
            SELECT 1
            FROM vendor_product_class_discounts discounts
            JOIN vendor_product_classes product_classes
                ON product_classes.id = discounts.product_class_id
            WHERE product_classes.vendor_id = :vendor_id
                AND discounts.id = vendor_product_class_discounts_future.discount_id
        )
        AND effective_date = :curr_eff_date
    ) as any_product_class_disc_future,
    EXISTS (
        SELECT 1
        FROM vendor_product_discounts_future
        WHERE EXISTS (
            SELECT 1
            FROM vendor_product_discounts discounts
            JOIN vendor_products products
                ON products.id = discounts.product_id
            WHERE products.vendor_id = :vendor_id
                AND discounts.id = vendor_product_discounts_future.discount_id
        )
        AND effective_date = :curr_eff_date
    ) as any_product_disc_future,
    EXISTS (
        SELECT 1
        FROM vendor_product_series_pricing_future
        WHERE EXISTS (
            SELECT 1
            FROM vendor_product_series_pricing series_pricing
            WHERE series_pricing.id = vendor_product_series_pricing_future.price_id
                AND series_pricing.vendor_id = :vendor_id
        )
        AND effective_date = :curr_eff_date
    ) as any_product_series_future;
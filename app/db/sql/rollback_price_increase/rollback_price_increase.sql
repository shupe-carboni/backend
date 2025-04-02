DO $$
DECLARE
    current_effective_date timestamp := :cur_eff_date;
    new_effective_date timestamp := :new_eff_date;
    target_vendor_id varchar := :vendor_id;
BEGIN

    -- 1. Move current vendor_pricing_by_class to future
    INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
    SELECT vpc.id, vpc.price, new_effective_date
    FROM vendor_pricing_by_class vpc
    WHERE vpc.effective_date = current_effective_date
    AND vpc.deleted_at IS NULL
    AND EXISTS (
        SELECT 1
        FROM vendor_products vp
        WHERE vp.id = vpc.product_id
        AND vp.vendor_id = target_vendor_id
    );

    -- 2. Move current vendor_pricing_by_customer to future
    INSERT INTO vendor_pricing_by_customer_future (price_id, price, effective_date)
    SELECT vpc.id, vpc.price, new_effective_date
    FROM vendor_pricing_by_customer vpc
    WHERE vpc.effective_date = current_effective_date
    AND vpc.deleted_at IS NULL
    AND EXISTS (
        SELECT 1
        FROM vendor_customers vc
        WHERE vc.id = vpc.vendor_customer_id
        AND vc.vendor_id = target_vendor_id
    );

    -- 3. Move current vendor_product_class_discounts to future
    INSERT INTO vendor_product_class_discounts_future (discount_id, discount, effective_date)
    SELECT vpcd.id, vpcd.discount, new_effective_date
    FROM vendor_product_class_discounts vpcd
    WHERE vpcd.effective_date = current_effective_date
    AND vpcd.deleted_at IS NULL
    AND EXISTS (
        SELECT 1
        FROM vendor_customers vc
        WHERE vc.id = vpcd.vendor_customer_id
        AND vc.vendor_id = target_vendor_id
    );

    -- 4. Move current vendor_product_discounts to future
    INSERT INTO vendor_product_discounts_future (discount_id, discount, effective_date)
    SELECT vpd.id, vpd.discount, new_effective_date
    FROM vendor_product_discounts vpd
    WHERE vpd.effective_date = current_effective_date
    AND vpd.deleted_at IS NULL
    AND EXISTS (
        SELECT 1
        FROM vendor_customers vc
        WHERE vc.id = vpd.vendor_customer_id
        AND vc.vendor_id = target_vendor_id
    );

    -- 5. Move current vendor_product_series_pricing to future
    INSERT INTO vendor_product_series_pricing_future (price_id, price, effective_date)
    SELECT vpsp.id, vpsp.price, new_effective_date
    FROM vendor_product_series_pricing vpsp
    WHERE vpsp.effective_date = current_effective_date
    AND vpsp.deleted_at IS NULL
    AND vpsp.vendor_id = target_vendor_id;

    -- 6. Update current tables with most recent historical data
    -- vendor_pricing_by_class
    UPDATE vendor_pricing_by_class vpc
    SET price = h.price,
        effective_date = h.effective_date
    FROM (
        SELECT vpc2.id, h.price, h.effective_date
        FROM vendor_pricing_by_class vpc2
        JOIN vendor_pricing_by_class_changelog h 
            ON h.vendor_pricing_by_class_id = vpc2.id
        WHERE vpc2.effective_date = current_effective_date
        AND vpc2.deleted_at IS NULL
        AND h.effective_date < current_effective_date
        AND h.timestamp = (
            SELECT MAX(timestamp)
            FROM vendor_pricing_by_class_changelog h2
            WHERE h2.vendor_pricing_by_class_id = vpc2.id
            AND h2.effective_date < current_effective_date
        )
        AND EXISTS (
            SELECT 1
            FROM vendor_products vp
            WHERE vp.id = vpc2.product_id
            AND vp.vendor_id = target_vendor_id
        )
    ) h
    WHERE vpc.id = h.id;

    -- vendor_pricing_by_customer
    UPDATE vendor_pricing_by_customer vpc
    SET price = h.price,
        effective_date = h.effective_date
    FROM (
        SELECT vpc2.id, h.price, h.effective_date
        FROM vendor_pricing_by_customer vpc2
        JOIN vendor_pricing_by_customer_changelog h
            ON h.vendor_pricing_by_customer_id = vpc2.id
        WHERE vpc2.effective_date = current_effective_date
        AND vpc2.deleted_at IS NULL
        AND h.effective_date < current_effective_date
        AND h.timestamp = (
            SELECT MAX(timestamp)
            FROM vendor_pricing_by_customer_changelog h2
            WHERE h2.vendor_pricing_by_customer_id = vpc2.id
            AND h2.effective_date < current_effective_date
        )
        AND EXISTS (
            SELECT 1
            FROM vendor_customers vc
            WHERE vc.id = vpc2.vendor_customer_id
            AND vc.vendor_id = target_vendor_id
        )
    ) h
    WHERE vpc.id = h.id;

    -- vendor_product_class_discounts
    UPDATE vendor_product_class_discounts vpcd
    SET discount = h.discount,
        effective_date = h.effective_date
    FROM (
        SELECT vpcd2.id, h.discount, h.effective_date
        FROM vendor_product_class_discounts vpcd2
        JOIN vendor_product_class_discounts_changelog h 
            ON h.vendor_product_class_discounts_id = vpcd2.id
        WHERE vpcd2.effective_date = current_effective_date
        AND vpcd2.deleted_at IS NULL
        AND h.effective_date < current_effective_date
        AND h.timestamp = (
            SELECT MAX(timestamp)
            FROM vendor_product_class_discounts_changelog h2
            WHERE h2.vendor_product_class_discounts_id = vpcd2.id
            AND h2.effective_date < current_effective_date
        )
        AND EXISTS (
            SELECT 1
            FROM vendor_customers vc
            WHERE vc.id = vpcd2.vendor_customer_id
            AND vc.vendor_id = target_vendor_id
        )
    ) h
    WHERE vpcd.id = h.id;

    -- vendor_product_discounts
    UPDATE vendor_product_discounts vpd
    SET discount = h.discount,
        effective_date = h.effective_date
    FROM (
        SELECT vpd2.id, h.discount, h.effective_date
        FROM vendor_product_discounts vpd2
        JOIN vendor_product_discounts_changelog h 
            ON h.vendor_product_discounts_id = vpd2.id
        WHERE vpd2.effective_date = current_effective_date
        AND vpd2.deleted_at IS NULL
        AND h.effective_date < current_effective_date
        AND h.timestamp = (
            SELECT MAX(timestamp)
            FROM vendor_product_discounts_changelog h2
            WHERE h2.vendor_product_discounts_id = vpd2.id
            AND h2.effective_date < current_effective_date
        )
        AND EXISTS (
            SELECT 1
            FROM vendor_customers vc
            WHERE vc.id = vpd2.vendor_customer_id
            AND vc.vendor_id = target_vendor_id
        )
    ) h
    WHERE vpd.id = h.id;

END $$;
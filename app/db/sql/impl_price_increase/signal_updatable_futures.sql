-- return a boolean array to determine which tables need to have updates
-- run against them
SELECT
    EXISTS (
        SELECT 1
        FROM vendor_pricing_by_class_future
        WHERE effective_date <= :today_date
    ) as any_class_pricing_future,
    EXISTS (
        SELECT 1
        FROM vendor_pricing_by_customer_future
        WHERE effective_date <= :today_date
    ) as any_customer_pricing_future,
    EXISTS (
        SELECT 1
        FROM vendor_product_class_discounts_future
        WHERE effective_date <= :today_date
    ) as any_product_class_disc_future,
    EXISTS (
        SELECT 1
        FROM vendor_product_discounts_future
        WHERE effective_date <= :today_date
    ) as any_product_disc_future,
    EXISTS (
        SELECT 1
        FROM vendor_product_series_pricing_future
        WHERE effective_date <= :today_date
    ) as any_product_series_future,
    EXISTS (
        SELECT 1
        FROM vendor_product_series_pricing_customer_effective_date_overrides
        WHERE effective_date <= :today_date
    ) as any_product_series_overrides;
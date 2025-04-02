WITH CurrentPricing AS (
    -- Get the current price and effective_date for the given vendor_id, series, and keys
    SELECT id AS price_id, price, effective_date, key
    FROM vendor_product_series_pricing
    WHERE vendor_id = :vendor_id
    AND series = :series
    AND deleted_at IS NULL
    AND (
        (:key_mode = 'exact' AND key = :key)
        OR(:key_mode = 'membership' AND 
            (
                CARDINALITY(CAST(:keys AS TEXT[])) > 0
                AND key IN (SELECT UNNEST(CAST(:keys AS TEXT[])))
            ))
        OR (:key_mode = 'first_2_parts' 
            AND :key is not null 
            AND :key ~ SUBSTRING(key FROM '^[^_]*_[^_]*_') )
        OR (:key_mode = 'regex' 
            AND :key is not null 
            AND :key ~ key)
        OR (:key_mode = 'adders' 
            AND key like 'adder_%')
    )
),
FuturePricing AS (
    -- Get future pricing if it exists and is beyond today
    SELECT f.price_id, f.price AS future_price, f.effective_date AS future_effective_date
    FROM vendor_product_series_pricing_future f
    WHERE f.price_id IN (SELECT price_id FROM CurrentPricing)
    AND f.effective_date > CURRENT_TIMESTAMP
),
OverrideCheck AS (
    -- Check if an override exists for the customer per price_id
    SELECT o.price_id, o.effective_date AS override_effective_date
    FROM vendor_product_series_pricing_customer_effective_date_overrides o
    WHERE o.price_id IN (SELECT price_id FROM CurrentPricing)
    AND o.vendor_customer_id = :customer_id
)
SELECT
    cp.key,
    -- Effective price: future price if it exists beyond today, otherwise current price
    COALESCE(fp.future_price, cp.price) AS effective_price,
    -- Effective date: override date if it exists, otherwise current effective_date
    COALESCE(oc.override_effective_date, cp.effective_date) AS effective_date
FROM CurrentPricing cp
LEFT JOIN FuturePricing fp ON cp.price_id = fp.price_id
LEFT JOIN OverrideCheck oc ON cp.price_id = oc.price_id;
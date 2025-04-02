WITH CurrentPricing AS (
    -- Get the current price for the given vendor_id, series, and keys
    SELECT id AS price_id, price, effective_date, key
    FROM vendor_product_series_pricing
    WHERE vendor_id = :vendor_id
    AND series = :series
    AND deleted_at IS NULL
    AND (
        :key_param IS NOT NULL 
        AND CASE :key_mode
            WHEN 'exact' THEN 
                CARDINALITY(:key_param) = 1 
                AND key = (:key_param)[1]
            WHEN 'membership' THEN 
                CARDINALITY(:key_param) > 0 
                AND key IN (SELECT UNNEST(:key_param))
            WHEN 'first_2_parts' THEN 
                CARDINALITY(:key_param) = 1 
                AND (:key_param)[1] ~ SUBSTRING(key FROM '^[^_]*_[^_]*_')
            WHEN 'regex' THEN 
                CARDINALITY(:key_param) = 1 
                AND (:key_param)[1] ~ key
            WHEN 'adders' THEN
                key like 'adder_%'
            ELSE FALSE  -- return no results
        END
    )
),
OverrideCheck AS (
    -- Check if an override exists for the customer per price_id
    SELECT o.price_id, o.effective_date AS override_effective_date
    FROM vendor_product_series_pricing_customer_effective_date_overrides o
    WHERE o.price_id IN (SELECT price_id FROM CurrentPricing)
    AND o.vendor_customer_id = :customer_id
),
FuturePricing AS (
    -- Get future pricing if it exists and is active as of today per price_id
    SELECT f.price_id, f.price, f.effective_date
    FROM vendor_product_series_pricing_future f
    WHERE f.price_id IN (SELECT price_id FROM CurrentPricing)
    AND f.effective_date <= CURRENT_TIMESTAMP
),
HistoryPricing AS (
    -- Get history records for each price_id, ranked by timestamp
    SELECT h.product_series_pricing_id AS price_id, h.price, h.effective_date, h.timestamp,
           ROW_NUMBER() OVER (PARTITION BY h.product_series_pricing_id ORDER BY h.timestamp DESC) AS rn,
           COUNT(*) OVER (PARTITION BY h.product_series_pricing_id) AS history_count
    FROM vendor_product_series_pricing_changelog h
    WHERE h.product_series_pricing_id IN (SELECT price_id FROM CurrentPricing)
)
SELECT
    cp.key,
    CASE
        -- Case 1: Override exists for this price_id
        WHEN oc.override_effective_date IS NOT NULL THEN
            COALESCE(
                -- Prefer history with earlier effective_date
                (SELECT hp.price
                 FROM HistoryPricing hp
                 WHERE hp.price_id = cp.price_id
                 AND hp.effective_date < cp.effective_date
                 ORDER BY hp.timestamp DESC
                 LIMIT 1),
                -- If only one history record and it matches current effective_date
                (SELECT hp.price
                 FROM HistoryPricing hp
                 WHERE hp.price_id = cp.price_id
                 AND hp.history_count = 1
                 AND hp.effective_date = cp.effective_date
                 LIMIT 1),
                -- Fallback to current if no valid history
                cp.price
            )
        -- Case 2: No override, future exists and is active
        WHEN fp.price IS NOT NULL THEN fp.price
        -- Case 3: No override, no future (or future not yet active)
        ELSE cp.price
    END AS effective_price,
    CASE
        -- Case 1: Override exists for this price_id
        WHEN oc.override_effective_date IS NOT NULL THEN
            COALESCE(
                -- Prefer history with earlier effective_date
                (SELECT hp.effective_date
                 FROM HistoryPricing hp
                 WHERE hp.price_id = cp.price_id
                 AND hp.effective_date < cp.effective_date
                 ORDER BY hp.timestamp DESC
                 LIMIT 1),
                -- If only one history record and it matches current effective_date, use it
                (SELECT hp.effective_date
                 FROM HistoryPricing hp
                 WHERE hp.price_id = cp.price_id
                 AND hp.history_count = 1
                 AND hp.effective_date = cp.effective_date
                 LIMIT 1),
                -- Fallback to current if no valid history
                cp.effective_date
            )
        -- Case 2: No override, future exists and is active
        WHEN fp.price IS NOT NULL THEN fp.effective_date
        -- Case 3: No override, no future (or future not yet active)
        ELSE cp.effective_date
    END AS effective_date
    -- *
FROM CurrentPricing cp
LEFT JOIN OverrideCheck oc ON cp.price_id = oc.price_id
LEFT JOIN FuturePricing fp ON cp.price_id = fp.price_id;
-- LEFT JOIN HistoryPricing hp ON cp.price_id = hp.price_id;
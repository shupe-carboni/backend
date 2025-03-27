INSERT INTO vendor_product_series_pricing_future (
    price_id,
    price,
    effective_date
)
SELECT key_pricing.id, new.price, new.effective_date
FROM vendor_product_series_pricing AS key_pricing
JOIN adp_product_series_pricing_update AS new
    ON new.vendor_id = key_pricing.vendor_id
    AND new.series = key_pricing.series
    AND new.key = key_pricing.key;

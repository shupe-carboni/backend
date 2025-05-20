UPDATE vendor_product_series_pricing_future
SET effective_date = :new_eff_date
WHERE EXISTS (
    SELECT 1
    FROM vendor_product_series_pricing series_pricing
    WHERE series_pricing.id = vendor_product_series_pricing_future.price_id
        AND series_pricing.vendor_id = :vendor_id
)
AND effective_date = :curr_eff_date ;
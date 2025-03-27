UPDATE vendor_product_series_pricing
SET price = future.price, effective_date = future.effective_date
FROM vendor_product_series_pricing_future as future
WHERE future.price_id = vendor_product_series_pricing.id
    AND future.effective_date::DATE <= :today_date
    AND vendor_product_series_pricing.deleted_at IS NULL;

DELETE FROM vendor_product_series_pricing_future 
WHERE effective_date::DATE <= :today_date;
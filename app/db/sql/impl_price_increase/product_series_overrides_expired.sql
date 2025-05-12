DELETE FROM vendor_product_series_pricing_customer_effective_date_overrides 
WHERE effective_date::DATE <= :today_date;
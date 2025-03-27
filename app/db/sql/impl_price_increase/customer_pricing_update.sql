UPDATE vendor_pricing_by_customer
SET price = future.price, effective_date = future.effective_date
FROM vendor_pricing_by_customer_future as future
WHERE future.price_id = vendor_pricing_by_customer.id
    AND future.effective_date::DATE <= :today_date
    AND vendor_pricing_by_customer.deleted_at IS NULL;

DELETE FROM vendor_pricing_by_customer_future 
WHERE effective_date::DATE <= :today_date;
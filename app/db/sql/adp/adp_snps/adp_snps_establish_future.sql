INSERT INTO vendor_product_discounts_future (
	discount_id,
	discount,
	effective_date
)
SELECT 
	class_price.id,
	(1-(new.price::float / class_price_future.price::float))*100, 
	:ed
FROM adp_snps AS new
JOIN vendor_customers vc
	ON vc.name = new.customer
	AND vc.vendor_id = 'adp'
JOIN vendor_products vp
	ON vp.vendor_product_identifier = new.description
	AND vp.vendor_id = 'adp'
JOIN vendor_pricing_by_class AS class_price
	ON class_price.product_id = vp.id
JOIN vendor_pricing_by_class_future AS class_price_future
	ON class_price_future.price_id = class_price.id
WHERE class_price_future.effective_date = :ed ;

INSERT INTO vendor_pricing_by_class_future (
	price_id,
	price,
	effective_date
)
SELECT 
	class_price.id, 
	new.price, 
	:ed
FROM vendor_pricing_by_class AS class_price
JOIN adp_zd AS new
	ON new.id = class_price.id;

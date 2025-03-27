INSERT INTO vendor_product_discounts (
	product_id, 
	vendor_customer_id,
	discount,
	effective_date
)
SELECT 
	vp.id,
	vc.id,
	(1-(new.price::float / class_price.price::float))*100,
	CURRENT_TIMESTAMP
FROM adp_snps AS new
JOIN vendor_customers vc
	ON vc.name = new.customer
	AND vc.vendor_id = 'adp'
JOIN vendor_products vp
	ON vp.vendor_product_identifier = new.description
	AND vp.vendor_id = 'adp'
JOIN vendor_pricing_by_class AS class_price
	ON class_price.product_id = vp.id
WHERE NOT EXISTS (
	select 1
	from vendor_product_discounts z
	where z.product_id = vp.id
	and z.vendor_customer_id = vc.id
);

INSERT INTO vendor_product_discounts (
	product_id, 
	vendor_customer_id,
	discount,
	effective_date,
	base_price_class,
	label_price_class
)
SELECT DISTINCT
	vp.id product_id,
	vc.id vendor_customer_id,
	(1-(new.price::float / class_price.price::float)) discount,
	CURRENT_TIMESTAMP effective_date,
	1 base_price_class,	-- == ZERO_DISCOUNT
	2 label_price_class	-- == STRATEGY_PRICING
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
	SELECT 1
	FROM vendor_product_discounts z
	WHERE z.product_id = vp.id
	AND z.vendor_customer_id = vc.id
) AND EXISTS (
	SELECT 1
	FROM vendor_pricing_classes price_class
	WHERE price_class.vendor_id = 'adp'
	AND price_class.id = class_price.pricing_class_id
	AND price_class.name = 'ZERO_DISCOUNT'
)

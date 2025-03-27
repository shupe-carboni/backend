INSERT INTO vendor_product_class_discounts_future (
	discount_id,
	discount,
	effective_date
)
SELECT vpc_discount.id, discount, :ed
FROM adp_mgds
JOIN vendor_product_classes vp_class
	ON vp_class.name = adp_mgds.mg
	AND vp_class.rank = 2
	AND vp_class.vendor_id = 'adp'
JOIN vendor_customers vc
	ON vc.name = adp_mgds.customer
	AND vc.vendor_id = 'adp';

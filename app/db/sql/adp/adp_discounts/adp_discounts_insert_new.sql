INSERT INTO vendor_product_class_discounts (
	product_class_id, vendor_customer_id, 
	discount, effective_date)
SELECT 
	vp_class.id,
	vc.id,
	new.discount,
	CURRENT_TIMESTAMP
FROM adp_mgds as new
JOIN vendor_product_classes vp_class
	ON vp_class.name = new.mg
	AND vp_class.rank = 2
	AND vp_class.vendor_id = 'adp'
JOIN vendor_customers vc
	ON vc.name = new.customer
	AND vc.vendor_id = 'adp'
WHERE NOT EXISTS (
	SELECT 1 
	FROM vendor_product_class_discounts a
	WHERE a.vendor_customer_id = vc.id
	    AND a.product_class_id = vp_class.id
)
RETURNING *;

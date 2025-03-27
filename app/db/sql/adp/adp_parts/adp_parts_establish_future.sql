-- preferred
INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
SELECT vpc.id, preferred, :ed
FROM adp_parts
JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = part_number
	AND vp.vendor_id = 'adp'
JOIN vendor_pricing_by_class vpc
	ON vpc.product_id = vp.id
WHERE EXISTS (
	SELECT 1
	FROM vendor_pricing_classes
	WHERE vendor_pricing_classes.id = vpc.pricing_class_id
		AND vendor_pricing_classes.vendor_id = 'adp'
		AND vendor_pricing_classes.name = 'PREFERRED_PARTS'
	);
-- standard
INSERT INTO vendor_pricing_by_class_future (price_id, price, effective_date)
SELECT vpc.id, standard, :ed
FROM adp_parts
JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = part_number
	AND vp.vendor_id = 'adp'
JOIN vendor_pricing_by_class vpc
	ON vpc.product_id = vp.id
WHERE EXISTS (
	SELECT 1
	FROM vendor_pricing_classes
	WHERE vendor_pricing_classes.id = vpc.pricing_class_id
		AND vendor_pricing_classes.vendor_id = 'adp'
		AND vendor_pricing_classes.name = 'STANDARD_PARTS'
	);

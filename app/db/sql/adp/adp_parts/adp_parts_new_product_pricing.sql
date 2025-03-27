-- preferred
INSERT INTO vendor_pricing_by_class (
	pricing_class_id,
	product_id, 
	price, 
	effective_date
)
SELECT (
	    SELECT id 
	    FROM vendor_pricing_classes 
	    WHERE vendor_id = 'adp' 
	    AND name = 'PREFERRED_PARTS'
	), 
	vp.id,
	preferred,
	CURRENT_TIMESTAMP
FROM adp_parts
JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = part_number
	AND vp.vendor_id = 'adp'
WHERE vp.id in :new_part_ids
	AND preferred IS NOT NULL;

-- standard
INSERT INTO vendor_pricing_by_class (
	pricing_class_id,
	product_id, 
	price, 
	effective_date
)
SELECT (
	    SELECT id 
	    FROM vendor_pricing_classes 
	    WHERE vendor_id = 'adp' 
	    AND name = 'STANDARD_PARTS'
	), 
	vp.id,
	standard,
	CURRENT_TIMESTAMP
FROM adp_parts
JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = part_number
	AND vp.vendor_id = 'adp'
WHERE vp.id in :new_part_ids
	AND standard IS NOT NULL;

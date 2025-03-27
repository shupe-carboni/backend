INSERT INTO vendor_product_attrs(vendor_product_id, attr, type, value)
SELECT vp.id, 'pkg_qty', 'NUMBER', adp_parts.pkg_qty
FROM adp_parts
JOIN vendor_products as vp
	ON vp.vendor_product_identifier = adp_parts.part_number
	AND vp.vendor_id = 'adp'
WHERE vp.id IN :new_part_ids

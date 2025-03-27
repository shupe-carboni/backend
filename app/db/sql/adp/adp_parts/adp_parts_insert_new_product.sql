INSERT INTO vendor_products (
	vendor_id,
	vendor_product_identifier,
	vendor_product_description
)
SELECT DISTINCT 'adp', part_number, description
FROM adp_parts
WHERE adp_parts.part_number NOT IN (
	SELECT DISTINCT vendor_product_identifier
	FROM vendor_products
	WHERE vendor_id = 'adp'
)
RETURNING id;

INSERT INTO vendor_customers (vendor_id, name)
SELECT 'adp' vendor_id, customer
FROM adp_customers
WHERE adp_customers.customer NOT IN (
	SELECT DISTINCT name
	FROM vendor_customers a
	WHERE vendor_id = 'adp'
);

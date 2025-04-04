-- not filtering by vendor because I'm supplying id's directly
SELECT vendor_product_id AS product_id, attr, value
FROM vendor_product_attrs
WHERE vendor_product_id IN :product_ids
    AND attr NOT IN ('category','private_label');
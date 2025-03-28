SELECT 
    product_id,
    price,
    effective_date
FROM vendor_pricing_by_class
WHERE EXISTS (
    SELECT 1 
    FROM vendor_products a 
    JOIN vendor_product_to_class_mapping b 
        ON b.product_id = a.id 
    JOIN vendor_product_classes c 
        ON c.id = b.product_class_id 
    WHERE c.name in :types 
        AND a.vendor_id = 'glasfloss' 
        AND a.id = vendor_pricing_by_class.product_id
        AND a.vendor_product_identifier = :model_number);
SELECT 
    pricing_by_customer_id as price_id,
    attr,
    value
FROM vendor_pricing_by_customer_attrs
WHERE pricing_by_customer_id IN :ids
    AND attr IN (
        'private_label',
        'ratings_ac_txv',
        'ratings_hp_txv',
        'ratings_field_txv',
        'ratings_piston',
        'sort_order'
    ); 
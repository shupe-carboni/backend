-- get customer-specific pricing
WITH product_attrs_agg AS (
    SELECT
        vendor_product_id as product_id,
        COALESCE(
            json_agg(
                json_build_object(
                    'id', id,
                    'attr', attr,
                    'type', type,
                    'value', value
                )
            )::jsonb,
            '[]'::jsonb
        ) as attrs
        FROM vendor_product_attrs
        GROUP BY vendor_product_id
), product_details as (
    SELECT 
        vp.id AS product_id,
        json_build_object(
            'id', vp.id,
            'part_id', vp.vendor_product_identifier,
            'description', vp.vendor_product_description,
            'categories', COALESCE(
                json_agg (
                    json_build_object(
                        'id', product_class.id,
                        'name', product_class.name,
                        'rank', product_class.rank
                    )
                ) FILTER (WHERE product_class.id IS NOT NULL)::jsonb,
                '[]'::jsonb
            ),
            'attrs', COALESCE(pa.attrs, '[]'::jsonb)
        )::jsonb AS product
    FROM vendor_products vp
    LEFT JOIN vendor_product_to_class_mapping vp_class_map
        ON vp_class_map.product_id = vp.id
    LEFT JOIN vendor_product_classes product_class
        ON product_class.id = vp_class_map.product_class_id
        AND product_class.vendor_id = :vendor_id
    LEFT JOIN product_attrs_agg as pa
        ON pa.product_id = vp.id
    WHERE vp.vendor_id = :vendor_id
    GROUP BY vp.id, vp.vendor_product_identifier, vp.vendor_product_description, pa.attrs
), formatted_pricing AS (
    SELECT 
        vpc.id as id,
        vpc.use_as_override as override,
        json_build_object(
            'id', vendor_pricing_classes.id,
            'name', vendor_pricing_classes.name
        )::jsonb as category,
        product_details.product,
        vpc.price,
        vpc.effective_date
    FROM vendor_pricing_by_customer vpc
    JOIN vendor_pricing_classes
        ON vendor_pricing_classes.id = vpc.pricing_class_id
        AND vendor_pricing_classes.vendor_id = :vendor_id
    LEFT JOIN product_details
        ON product_details.product_id = vpc.product_id
    WHERE EXISTS (
        SELECT 1
        FROM vendor_customers a
        where a.id = :customer_id
        AND a.id = vpc.vendor_customer_id
        AND a.vendor_id = :vendor_id
    )
)
SELECT 
    formatted_pricing.id,
    formatted_pricing.override,
    category,
    product,
    formatted_pricing.price,
    formatted_pricing.effective_date,
    json_agg(
        json_build_object(
            'id', h.id,
            'price', h.price,
            'effective_date', h.effective_date,
            'timestamp', h.timestamp
        )
    ) as history,
    COALESCE(
        json_agg(
            json_build_object(
                'id', notes.id,
                'attr', notes.attr,
                'type', notes.type,
                'value', notes.value
            )
        )::jsonb,
        '[]'::jsonb
    ) as notes
FROM formatted_pricing
LEFT JOIN vendor_pricing_by_customer_changelog AS h
    ON vendor_pricing_by_customer_id = formatted_pricing.id
LEFT JOIN vendor_pricing_by_customer_attrs AS notes
    ON notes.pricing_by_customer_id = formatted_pricing.id
GROUP BY 
    formatted_pricing.id, 
    formatted_pricing.override,
    category,
    product,
    formatted_pricing.price,
    formatted_pricing.effective_date;
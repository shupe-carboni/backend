-- get customer-specific pricing as nested JSON
WITH notes_agg AS (
    SELECT
        pricing_by_customer_id,
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
        ) AS notes
    FROM vendor_pricing_by_customer_attrs
    WHERE deleted_at IS NULL
    GROUP BY pricing_by_customer_id
), product_attrs_agg AS (
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
        WHERE deleted_at IS NULL
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
        AND vp.deleted_at IS NULL
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
    JOIN product_details
        ON product_details.product_id = vpc.product_id
    WHERE EXISTS (
        SELECT 1
        FROM vendor_customers a
        WHERE a.id = :customer_id
            AND a.id = vpc.vendor_customer_id
            AND a.vendor_id = :vendor_id
            AND a.deleted_at IS NULL
    )
    AND vpc.deleted_at IS NULL
), with_future_price AS (
    SELECT
        formatted_pricing.id,
        formatted_pricing.override,
        category,
        product,
        formatted_pricing.price,
        formatted_pricing.effective_date,
        COALESCE( na.notes, '[]'::jsonb) as notes,
        CASE
            WHEN future.price IS NULL
            THEN NULL
            ELSE json_build_object(
                'price', future.price,
                'effective_date', future.effective_date
            )::jsonb
            END as future
        FROM formatted_pricing
        LEFT JOIN vendor_pricing_by_customer_future as future
            ON future.price_id = formatted_pricing.id
        LEFT JOIN notes_agg AS na
            ON na.pricing_by_customer_id = formatted_pricing.id
)
SELECT 
    with_future_price.*,
    json_agg(
        json_build_object(
            'id', h.id,
            'price', h.price,
            'effective_date', h.effective_date,
            'timestamp', h.timestamp
        )
    ) as history
FROM with_future_price
LEFT JOIN vendor_pricing_by_customer_changelog AS h
    ON vendor_pricing_by_customer_id = with_future_price.id
GROUP BY 
    with_future_price.id, 
    with_future_price.override,
    with_future_price.category,
    with_future_price.product,
    with_future_price.price,
    with_future_price.effective_date,
    with_future_price.future,
    with_future_price.notes;
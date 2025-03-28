WITH glasfloss_pricing_mto AS (
    SELECT 
        id,
        series,
        split_part(key,'_',1) as size_type,
        split_part(key,'_',2) as part_number,
        split_part(key,'_',3)::float / 100 as depth,
        split_part(key,'_',4)::int as upper_bnd_face_area,
        price
    FROM vendor_product_series_pricing
    WHERE vendor_id = 'glasfloss'
)
SELECT price, part_number
FROM glasfloss_pricing_mto
WHERE series = :series
    AND size_type = :size_type
    AND depth = :depth
    AND upper_bnd_face_area = (
        SELECT MIN(upper_bnd_face_area)
        FROM glasfloss_pricing_mto
        WHERE upper_bnd_face_area >= :face_area
            AND series = :series
            AND size_type = :size_type
    );
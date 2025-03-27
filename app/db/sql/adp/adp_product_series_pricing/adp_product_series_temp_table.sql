DROP TABLE IF EXISTS adp_product_series_pricing_update;
CREATE TEMPORARY TABLE adp_product_series_pricing_update (
    vendor_id varchar,
    series varchar,
    key varchar,
    price int,
    effective_date timestamp
);
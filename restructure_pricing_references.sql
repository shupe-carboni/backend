BEGIN;
CREATE TABLE vendor_product_series_pricing (
    id SERIAL PRIMARY KEY,
    vendor_id varchar,
    series varchar,
    key varchar,
    price int,
    effective_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vendor_product_series_pricing_changelog (
    id SERIAL PRIMARY KEY,
    product_series_pricing_id int,
    price int,
    effective_date TIMESTAMP,
    "timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Changelog
	-- new values
	CREATE OR REPLACE FUNCTION vendor_product_series_pricing_insert_fn()
	RETURNS TRIGGER AS $$
	BEGIN
		INSERT INTO vendor_product_series_pricing_changelog (product_series_pricing_id, price, effective_date)
		VALUES (NEW.id, NEW.price, NEW.effective_date);
		RETURN NEW;
	END;
	$$ LANGUAGE plpgsql;
	CREATE TRIGGER vendor_product_series_pricing_insert
	AFTER INSERT ON vendor_product_series_pricing
	FOR EACH ROW
	EXECUTE FUNCTION vendor_product_series_pricing_insert_fn();
	-- updates
	CREATE OR REPLACE FUNCTION vendor_product_series_pricing_update_fn()
	RETURNS TRIGGER AS $$
	BEGIN
		IF OLD.price != NEW.price OR OLD.effective_date != NEW.effective_date THEN
		    INSERT INTO vendor_product_series_pricing_changelog (product_series_pricing_id, price, effective_date)
			VALUES (OLD.id, NEW.price, NEW.effective_date);
		END IF;
		RETURN NEW;
	END;
	$$ LANGUAGE plpgsql;
	CREATE TRIGGER vendor_product_series_pricing_update
	BEFORE UPDATE ON vendor_product_series_pricing
	FOR EACH ROW
	EXECUTE FUNCTION vendor_product_series_pricing_update_fn();

-- B series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'B' series, 
    ((tonnage::varchar) || '_' || slab || '_base') as "key",
    base*100 as price
FROM adp_pricing_b_series
WHERE base IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'B' series, 
    ((tonnage::varchar) || '_' || slab || '_2') as "key",
    "2"*100 as price
FROM adp_pricing_b_series
WHERE "2" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'B' series, 
    ((tonnage::varchar) || '_' || slab || '_3') as "key",
    "3"*100 as price
FROM adp_pricing_b_series
WHERE "3" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'B' series, 
    ((tonnage::varchar) || '_' || slab || '_4') as "key",
    "4"*100 as price
FROM adp_pricing_b_series
WHERE "4" IS NOT NULL;

-- CP series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'CP' series, 
    "C" as "key",
    price*100 as price
FROM adp_pricing_cp_series
WHERE "C" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'CP' series, 
    "A" as "key",
    price*100 as price
FROM adp_pricing_cp_series
WHERE "A" IS NOT NULL;

-- F series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'F' series, 
    ((tonnage::varchar) || '_' || slab || '_base') as "key",
    "base"*100 as price
FROM adp_pricing_f_series
WHERE "base" IS NOT NULL and "base" > 0;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'F' series, 
    ((tonnage::varchar) || '_' || slab || '_05') as "key",
    "05"*100 as price
FROM adp_pricing_f_series
WHERE "05" IS NOT NULL and "05" > 0;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'F' series, 
    ((tonnage::varchar) || '_' || slab || '_07') as "key",
    "07"*100 as price
FROM adp_pricing_f_series
WHERE "07" IS NOT NULL and "07" > 0;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'F' series, 
    ((tonnage::varchar) || '_' || slab || '_10') as "key",
    "10"*100 as price
FROM adp_pricing_f_series
WHERE "10" IS NOT NULL and "10" > 0;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'F' series, 
    ((tonnage::varchar) || '_' || slab || '_15') as "key",
    "15"*100 as price
FROM adp_pricing_f_series
WHERE "15" IS NOT NULL AND "15" > 0;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'F' series, 
    ((tonnage::varchar) || '_' || slab || '_20') as "key",
    "20"*100 as price
FROM adp_pricing_f_series
WHERE "20" IS NOT NULL AND "20" > 0;

-- HD series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HD' series, 
    (slab::varchar || '_embossed') as "key",
    "embossed"*100 as price
FROM adp_pricing_hd_series
WHERE "embossed" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HD' series, 
    (slab::varchar || '_painted') as "key",
    "painted"*100 as price
FROM adp_pricing_hd_series
WHERE "painted" IS NOT NULL;

-- HE series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HE' series, 
    (slab::varchar || '_uncased') as "key",
    "uncased"*100 as price
FROM adp_pricing_he_series
WHERE "uncased" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HE' series, 
    (slab::varchar || '_embossed_cased') as "key",
    "EMBOSSED_CASED"*100 as price
FROM adp_pricing_he_series
WHERE "EMBOSSED_CASED" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HE' series, 
    (slab::varchar || '_painted_cased') as "key",
    "PAINTED_CASED"*100 as price
FROM adp_pricing_he_series
WHERE "PAINTED_CASED" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HE' series, 
    (slab::varchar || '_embossed_mp') as "key",
    "EMBOSSED_MP"*100 as price
FROM adp_pricing_he_series
WHERE "EMBOSSED_MP" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HE' series, 
    (slab::varchar || '_painted_mp') as "key",
    "PAINTED_MP"*100 as price
FROM adp_pricing_he_series
WHERE "PAINTED_MP" IS NOT NULL;

-- HH series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'HH' series, 
    slab::varchar as "key",
    "price"*100 as price
FROM adp_pricing_hh_series
WHERE "price" IS NOT NULL;

-- MH series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'MH' series, 
    slab::varchar as "key",
    "price"*100 as price
FROM adp_pricing_mh_series
WHERE "price" IS NOT NULL;

-- S series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'S' series, 
    SUBSTRING(model FROM 2 FOR 2) || "00" as "key",
    "00"*100 as price
FROM adp_pricing_s_series
WHERE "00" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'S' series, 
    SUBSTRING(model FROM 2 FOR 2) || "05" as "key",
    "05"*100 as price
FROM adp_pricing_s_series
WHERE "05" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'S' series, 
    SUBSTRING(model FROM 2 FOR 2) || "07" as "key",
    "07"*100 as price
FROM adp_pricing_s_series
WHERE "07" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'S' series, 
    SUBSTRING(model FROM 2 FOR 2) || "10" as "key",
    "10"*100 as price
FROM adp_pricing_s_series
WHERE "10" IS NOT NULL;

-- SC series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
select 
    'adp' vendor_id,
    'SC' series, 
    model || '_0' as "key",
    "0"*100 as price
from adp_pricing_sc_series
where "0" is not null and "0" != 0;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
SELECT 
    'adp' vendor_id,
    'SC' series, 
    model || '_1' as "key",
    "1"*100 as price
FROM adp_pricing_sc_series
WHERE "1" IS NOT NULL and "1" != 0;

-- V series
INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
select 
    'adp' vendor_id,
    'V' series, 
    slab || '_embossed' as "key",
    "EMBOSSED"*100 as price
from adp_pricing_v_series
WHERE "EMBOSSED" IS NOT NULL;

INSERT INTO vendor_product_series_pricing(vendor_id, series, "key", price)
select 
    'adp' vendor_id,
    'V' series, 
    slab || '_painted' as "key",
    "PAINTED"*100 as price
from adp_pricing_v_series
WHERE "PAINTED" IS NOT NULL;

COMMIT;

ALTER TABLE vendor_product_series_pricing
ALTER COLUMN vendor_id SET NOT NULL,
ALTER COLUMN series SET NOT NULL,
ALTER COLUMN key SET NOT NULL;

ALTER TABLE vendor_product_series_pricing
ADD CONSTRAINT unique_vendor_series_key
UNIQUE (vendor_id, series, key);
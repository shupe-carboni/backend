-- NEW TABLES
CREATE TABLE vendors (
	name VARCHAR,
	headquarters VARCHAR,
	description TEXT,
	phone BIGINT,
	logo_path VARCHAR,
	id VARCHAR PRIMARY KEY);
-- customers
CREATE TABLE vendor_customers (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	name VARCHAR);
CREATE TABLE vendor_customer_attrs (
	id SERIAL PRIMARY KEY,
	vendor_customer_id INT REFERENCES vendor_customers(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	UNIQUE (vendor_customer_id, attr, type, value));

-- products
CREATE TABLE vendor_products (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	vendor_product_identifier VARCHAR,
	vendor_product_description VARCHAR);
CREATE TABLE vendor_product_classes (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	name VARCHAR,
	rank INT);
CREATE TABLE vendor_product_to_class_mapping (
	id SERIAL PRIMARY KEY,
	product_class_id INT REFERENCES vendor_product_classes(id),
	product_id INT REFERENCES vendor_products(id));
CREATE TABLE vendor_product_attrs (
	id SERIAL PRIMARY KEY,
	vendor_product_id INT REFERENCES vendor_products(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR);

-- pricing
CREATE TABLE vendor_pricing_classes (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	name VARCHAR, UNIQUE(vendor_id, name));
CREATE TABLE vendor_pricing_by_class (
	id SERIAL PRIMARY KEY,
	pricing_class_id INT REFERENCES vendor_pricing_classes(id),
	product_id INT REFERENCES vendor_products(id),
	price INT);
CREATE TABLE vendor_pricing_by_customer (
	id SERIAL PRIMARY KEY,
	product_id INT REFERENCES vendor_products(id),
	pricing_class_id INT REFERENCES vendor_pricing_classes(id),
	vendor_customer_id INT REFERENCES vendor_customers(id),
	use_as_override BOOLEAN DEFAULT false,
	price INT);
CREATE TABLE vendor_product_class_discounts (
	id SERIAL PRIMARY KEY,
	product_class_id INT REFERENCES vendor_product_classes(id),
	vendor_customer_id INT REFERENCES vendor_customers(id),
	discount FLOAT);
CREATE TABLE vendor_customer_pricing_classes (
	id SERIAL PRIMARY KEY,
	pricing_class_id INT REFERENCES vendor_pricing_classes(id),
	vendor_customer_id INT REFERENCES vendor_customers(id));
CREATE TABLE vendor_pricing_by_customer_attrs (
	id SERIAL PRIMARY KEY,
	pricing_by_customer_id INT REFERENCES vendor_pricing_by_customer(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	UNIQUE (pricing_by_customer_id, attr, type, value));

-- quotes
CREATE TABLE vendor_quotes (
	id SERIAL PRIMARY KEY,
	vendor_customer_id INT REFERENCES vendor_customers(id),
	place_id INT REFERENCES sca_places(id),
	vendor_quote_number VARCHAR,
	job_name VARCHAR,
	status stage,
	quote_doc VARCHAR,
	plans_doc VARCHAR);
CREATE TABLE vendor_quotes_attrs (
	id SERIAL PRIMARY KEY,
	vendor_quotes_id INT REFERENCES vendor_quotes(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	UNIQUE (vendor_quotes_id, attr, type, value));
CREATE TABLE vendor_quote_products (
	id SERIAL PRIMARY KEY,
	vendor_quotes_id INT REFERENCES vendor_quotes(id),
	product_id INT REFERENCES vendor_products(id),
	tag VARCHAR,
	competitor_model VARCHAR,
	qty INT,
	price INT);

-- favoriting
CREATE TABLE customer_pricing_by_customer (
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES sca_users(id),
	pricing_by_customer_id INT REFERENCES vendor_pricing_by_customer(id));
CREATE TABLE customer_pricing_by_class (
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES sca_users(id),
	pricing_by_class_id INT REFERENCES vendor_pricing_by_class(id));

-- mapping to customers
CREATE TABLE customer_location_mapping (
	id SERIAL PRIMARY KEY,
	vendor_customer_id INT REFERENCES vendor_customers(id),
	customer_location_id INT REFERENCES sca_customer_locations(id));

-- MOVE DATA
-- vendors
INSERT INTO vendors
SELECT * FROM sca_vendors;
-- customers
-- adp
INSERT INTO vendor_customers (vendor_id, name)
	SELECT 'adp' AS vendor, adp_alias AS name
	FROM adp_customers;
-- friedrich
INSERT INTO vendor_customers (vendor_id, name)
	SELECT 'friedrich' AS vendor, name
	FROM friedrich_customers;
INSERT INTO vendor_customer_attrs (vendor_customer_id, attr, type, value)
	SELECT b.id vendor_customer_id, 'account_number' AS attr,
		'BIGINT' AS type, friedrich_acct_number::VARCHAR AS value
	FROM friedrich_customers a
	JOIN vendor_customers b
	ON b.name = a.name
	AND b.vendor_id = 'friedrich';

-- customer location mapping
-- ADP is the only one with data, so we can start with just them 
-- and keep id numbers consistent
INSERT INTO customer_location_mapping (vendor_customer_id, customer_location_id)
	SELECT DISTINCT vc.id, a.sca_customer_location_id
	FROM adp_alias_to_sca_customer_locations AS a
	JOIN adp_customers AS ac
	ON ac.id = a.adp_customer_id
	JOIN vendor_customers AS vc
	ON vc.name = ac.adp_alias;

-- customer terms
INSERT INTO vendor_customer_attrs (vendor_customer_id, attr, type, value)
	SELECT DISTINCT d.vendor_customer_id, 'ppf', 'NUMBER', ppf
	FROM adp_customer_terms AS a
	JOIN sca_customers AS b
	ON b.id = a.sca_id
	JOIN sca_customer_locations AS c
	ON c.customer_id = b.id
	JOIN customer_location_mapping AS d
	ON d.customer_location_id = c.id;

INSERT INTO vendor_customer_attrs (vendor_customer_id, attr, type, value)
	SELECT DISTINCT d.vendor_customer_id, 'terms', 'STRING', terms
	FROM adp_customer_terms AS a
	JOIN sca_customers AS b
	ON b.id = a.sca_id
	JOIN sca_customer_locations AS c
	ON c.customer_id = b.id
	JOIN customer_location_mapping AS d
	ON d.customer_location_id = c.id;

-- products
-- adp
INSERT INTO vendor_products (vendor_id, vendor_product_identifier)
	SELECT DISTINCT 'adp', model_number
	FROM adp_coil_programs;
INSERT INTO vendor_products (vendor_id, vendor_product_identifier)
	SELECT DISTINCT 'adp', model_number
	FROM adp_ah_programs;
INSERT INTO vendor_products (vendor_id, vendor_product_identifier, vendor_product_description)
	SELECT DISTINCT 'adp', adppp.part_number::VARCHAR, adppp.description
	FROM adp_pricing_parts AS adppp;
-- friedrich
INSERT INTO vendor_products (vendor_id, vendor_product_identifier, vendor_product_description)
	SELECT DISTINCT 'friedrich', f.model_number, f.description
	FROM friedrich_products f;

-- the product features need tp be unraveled from columns to rows
-- coil str type attrs proposed coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id,
		unnest(array['category','private_label','mpg',
			'series','metering','cabinet',
			'ratings_ac_txv','ratings_hp_txv',
			'ratings_piston', 'ratings_field_txv']) AS attr,
		'STRING' AS "type",
		unnest(array[category,private_label,mpg,series,metering,
			cabinet,ratings_ac_txv,ratings_hp_txv,
			ratings_piston, ratings_field_txv]) value
	FROM adp_coil_programs a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number
	WHERE stage::VARCHAR = 'PROPOSED';

-- coil str type attrs active coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id,
		unnest(array['category','private_label','mpg',
			'series','metering','cabinet',
			'ratings_ac_txv','ratings_hp_txv',
			'ratings_piston', 'ratings_field_txv']) AS attr,
		'STRING' AS "type",
		unnest(array[category,private_label,mpg,series,metering,
			cabinet,ratings_ac_txv,ratings_hp_txv
			,ratings_piston, ratings_field_txv]) value
	FROM adp_coil_programs a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number
	WHERE stage::VARCHAR = 'ACTIVE'
	AND a.model_number NOT IN (
		SELECT DISTINCT model_number
		FROM adp_coil_programs
		WHERE stage::VARCHAR = 'PROPOSED');

-- ah str type attrs proposed coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id,
		unnest(array['category','private_label','mpg',
			'series','metering','motor','heat',
			'ratings_ac_txv','ratings_hp_txv',
			'ratings_piston', 'ratings_field_txv']) AS attr,
		'STRING' AS "type",
		unnest(array[category,private_label,mpg,series,
			metering,motor,heat,ratings_ac_txv,
			ratings_hp_txv,ratings_piston,
			ratings_field_txv]) value
	FROM adp_ah_programs a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number
	WHERE stage::VARCHAR = 'PROPOSED';

-- ah str type attrs active coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id,
		unnest(array['category','private_label','mpg',
			'series','metering','motor','heat',
			'ratings_ac_txv','ratings_hp_txv',
			'ratings_piston', 'ratings_field_txv']) AS attr,
		'STRING' AS "type",
		unnest(array[category,private_label,mpg,series,metering,
			motor,heat,ratings_ac_txv,ratings_hp_txv,
			ratings_piston, ratings_field_txv]) value
	FROM adp_ah_programs a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number
	WHERE stage::VARCHAR = 'ACTIVE'
	AND a.model_number NOT IN (
		SELECT DISTINCT model_number 
		FROM adp_coil_programs
		WHERE stage::VARCHAR = 'PROPOSED');

-- coil numeric type attrs active coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id,
		unnest(array['pallet_qty','tonnage','width',
			'depth','height','length','weight']) AS attr,
		'NUMBER' AS "type",
		unnest(array[pallet_qty, tonnage, width,
			depth, height, length, weight]) value 
	FROM adp_coil_programs a 
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number 
	WHERE stage::VARCHAR = 'ACTIVE'
	AND a.model_number NOT IN (
		SELECT DISTINCT model_number 
		FROM adp_coil_programs
		WHERE stage::VARCHAR = 'PROPOSED');

-- ah numeric type attrs active coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id, 
		unnest(array['pallet_qty','min_qty','tonnage',
			'width','depth','height','weight']) AS attr,
		'NUMBER' AS "type",
		unnest(array[pallet_qty, min_qty,tonnage, width,
			depth, height, weight]) value
	FROM adp_ah_programs a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number
	WHERE stage::VARCHAR = 'ACTIVE'
	AND a.model_number NOT IN (
		SELECT DISTINCT model_number
		FROM adp_coil_programs
		WHERE stage::VARCHAR = 'PROPOSED');

-- coil numeric type attrs proposed coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id,
		unnest(array['pallet_qty','tonnage','width',
			'depth','height','length','weight']) AS attr,
		'NUMBER' AS "type",
		unnest(array[pallet_qty, tonnage, width,
			depth, height, length, weight]) value 
	FROM adp_coil_programs a 
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number 
	WHERE stage::VARCHAR = 'PROPOSED';

-- ah numeric type attrs proposed coils
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id, 
		unnest(array['pallet_qty','min_qty','tonnage',
			'width','depth','height','weight']) AS attr,
		'NUMBER' AS "type",
		unnest(array[pallet_qty, min_qty,tonnage, width,
			depth, height, weight]) value
	FROM adp_ah_programs a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.model_number
	WHERE stage::VARCHAR = 'PROPOSED';

-- parts attrs
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT vp.id, 'pkg_qty', 'NUMBER', pkg_qty
	FROM adp_pricing_parts
	JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = part_number::VARCHAR;

-- adp product categories and material groups as product classes
INSERT INTO vendor_product_classes (vendor_id, name, rank)
	VALUES ('adp', 'Coils', 1),
		   ('adp', 'AH', 1),
		   ('adp', 'UH', 1),
		   ('adp', 'Parts', 1),
		   ('adp', 'Accessory', 1);

INSERT INTO vendor_product_classes (vendor_id, name, rank)
	SELECT 'adp' AS vendor_id, id::VARCHAR AS name, 2 AS rank
	FROM adp_material_groups;

-- assign ADP products to classes in the class mapping
INSERT INTO vendor_product_to_class_mapping (product_class_id, product_id)
	SELECT pc.id, p.id
	FROM vendor_product_classes AS pc
	JOIN (
		SELECT vp.id, vpa.value 
		FROM vendor_products AS vp
		JOIN vendor_product_attrs AS vpa
		ON vp.id = vpa.vendor_product_id
		WHERE vpa.attr = 'mpg') AS p 
	ON p.value = pc.name;

-- migrate adp material group discounts to vendor product class discounts
INSERT INTO vendor_product_class_discounts (product_class_id, vendor_customer_id, discount)
	SELECT pc.id, vc.id, adpmgd.discount
	FROM adp_material_group_discounts AS adpmgd
	JOIN vendor_product_classes AS pc
	ON pc.name = adpmgd.mat_grp::VARCHAR
	JOIN adp_customers AS ac
	ON ac.id = adpmgd.customer_id
	JOIN vendor_customers AS vc
	ON vc.name = ac.adp_alias;
-- price classes
INSERT INTO vendor_pricing_classes (vendor_id, name)
	VALUES ('adp', 'ZERO_DISCOUNT'),
		   ('adp', 'STRATEGY_PRICING'),
		   ('adp', 'PREFERRED_PARTS'),
		   ('adp', 'STANDARD_PARTS'),
		   ('friedrich', 'STANDARD'),
		   ('friedrich', 'STOCKING'),
		   ('friedrich', 'NON_STOCKING');
-- pricing by class 
-- adp
-- preferred parts
INSERT INTO vendor_pricing_by_class (pricing_class_id, product_id, price)
	SELECT vpc.id, vp.id, (adppp.preferred*100)::INT
	FROM adp_pricing_parts AS adppp
	JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = adppp.part_number
	JOIN vendors AS v
	ON v.id = vp.vendor_id
	JOIN vendor_pricing_classes AS vpc
	ON vpc.vendor_id = v.id
	WHERE v.id = 'adp'
	AND vpc.name = 'PREFERRED_PARTS';

-- standard parts
INSERT INTO vendor_pricing_by_class (pricing_class_id, product_id, price)
	SELECT vpc.id, vp.id, (adppp.standard*100)::INT
	FROM adp_pricing_parts AS adppp
	JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = adppp.part_number
	JOIN vendors AS v
	ON v.id = vp.vendor_id
	JOIN vendor_pricing_classes AS vpc
	ON vpc.vendor_id = v.id
	WHERE v.id = 'adp'
	AND vpc.name = 'STANDARD_PARTS';
-- zero discount coils
INSERT INTO vendor_pricing_by_class (pricing_class_id, product_id, price)
	SELECT DISTINCT vpc.id, vp.id, (acp.zero_discount_price*100)::INT
	FROM adp_coil_programs AS acp
	JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = acp.model_number
	JOIN vendors AS v
	ON v.id = vp.vendor_id
	JOIN vendor_pricing_classes AS vpc
	ON vpc.vendor_id = v.id
	WHERE v.id = 'adp'
	AND vpc.name = 'ZERO_DISCOUNT'
	AND acp.stage::VARCHAR IN ('ACTIVE','PENDING');
-- zero discount air handlers
INSERT INTO vendor_pricing_by_class (pricing_class_id, product_id, price)
	SELECT DISTINCT vpc.id, vp.id, (ahp.zero_discount_price*100)::INT
	FROM adp_ah_programs AS ahp
	JOIN vendor_products AS vp
	ON vp.vendor_product_identifier = ahp.model_number
	JOIN vendors AS v
	ON v.id = vp.vendor_id
	JOIN vendor_pricing_classes AS vpc
	ON vpc.vendor_id = v.id
	WHERE v.id = 'adp'
	AND vpc.name = 'ZERO_DISCOUNT'
	AND ahp.stage::VARCHAR IN ('ACTIVE','PENDING');

-- friedrich
INSERT INTO vendor_pricing_by_class (pricing_class_id, product_id, price)
	SELECT DISTINCT vpc.id, p.id, (a.price*100)::INT
	FROM friedrich_pricing a
	JOIN friedrich_products b ON a.model_number_id = b.id
	JOIN vendor_products p ON p.vendor_product_identifier = b.model_number
	JOIN vendors v ON v.id = p.vendor_id
	JOIN vendor_pricing_classes vpc ON vpc.vendor_id = v.id AND vpc.name = a.price_level::VARCHAR
	WHERE v.id = 'friedrich';

-- pricing by customer (using pricing class as a tag)
-- adp snps
INSERT INTO vendor_pricing_by_customer (product_id, pricing_class_id, vendor_customer_id, use_as_override, price)
	SELECT DISTINCT p.id, pc.id, vc.id, true, (snp_price*100)::INT
	FROM adp_coil_programs AS a
	JOIN vendor_products AS p ON p.vendor_product_identifier = a.model_number
	JOIN vendors AS v ON v.id = p.vendor_id
	JOIN vendor_pricing_classes AS pc ON pc.vendor_id = v.id
	JOIN vendor_customers AS vc ON vc.vendor_id = v.id
	JOIN adp_customers AS b ON b.adp_alias = vc.name
	WHERE pc.name = 'STRATEGY_PRICING'
	AND v.id = 'adp'
	AND a.snp_price IS NOT NULL;
-- adp material group discount pricing
INSERT INTO vendor_pricing_by_customer (product_id, pricing_class_id, vendor_customer_id, use_as_override, price)
	SELECT DISTINCT p.id, pc.id, vc.id, true, (material_group_net_price*100)::INT
	FROM adp_coil_programs AS a
	JOIN vendor_products AS p ON p.vendor_product_identifier = a.model_number
	JOIN vendors AS v ON v.id = p.vendor_id
	JOIN vendor_pricing_classes AS pc ON pc.vendor_id = v.id
	JOIN vendor_customers AS vc ON vc.vendor_id = v.id
	JOIN adp_customers AS b ON b.adp_alias = vc.name
	WHERE pc.name = 'STRATEGY_PRICING'
	AND v.id = 'adp'
	AND a.material_group_net_price IS NOT NULL
	AND a.snp_price IS NULL;

-- customer pricing classes
-- adp preferred parts
INSERT INTO vendor_customer_pricing_classes (pricing_class_id, vendor_customer_id)
	SELECT DISTINCT vpc.id, vc.id
	FROM adp_customers a
	JOIN vendor_customers vc ON vc.name = a.adp_alias
	JOIN vendors v ON v.id = vc.vendor_id
	JOIN vendor_pricing_classes vpc ON v.id = vpc.vendor_id
	WHERE v.id = 'adp'
	AND vpc.name = 'PREFERRED_PARTS'
	AND a.preferred_parts;
-- adp standard parts
INSERT INTO vendor_customer_pricing_classes (pricing_class_id, vendor_customer_id)
	SELECT DISTINCT vpc.id, vc.id
	FROM adp_customers a
	JOIN vendor_customers vc ON vc.name = a.adp_alias
	JOIN vendors v ON v.id = vc.vendor_id
	JOIN vendor_pricing_classes vpc ON v.id = vpc.vendor_id
	WHERE v.id = 'adp'
	AND vpc.name = 'STANDARD_PARTS'
	AND NOT a.preferred_parts;
-- adp zero discount
INSERT INTO vendor_customer_pricing_classes (pricing_class_id, vendor_customer_id)
	SELECT DISTINCT vpc.id, vc.id
	FROM adp_customers a
	JOIN vendor_customers vc ON vc.name = a.adp_alias
	JOIN vendors v ON v.id = vc.vendor_id
	JOIN vendor_pricing_classes vpc ON v.id = vpc.vendor_id
	WHERE v.id = 'adp'
	AND vpc.name = 'ZERO_DISCOUNT';
-- adp strategy
INSERT INTO vendor_customer_pricing_classes (pricing_class_id, vendor_customer_id)
	SELECT DISTINCT vpc.id, vc.id
	FROM adp_customers a
	JOIN vendor_customers vc ON vc.name = a.adp_alias
	JOIN vendors v ON v.id = vc.vendor_id
	JOIN vendor_pricing_classes vpc ON v.id = vpc.vendor_id
	WHERE v.id = 'adp'
	AND vpc.name = 'STRATEGY_PRICING';
-- friedrich
INSERT INTO vendor_customer_pricing_classes (pricing_class_id, vendor_customer_id)
	SELECT DISTINCT vpc.id, vc.id
	FROM friedrich_customers a
	JOIN vendor_customers vc ON vc.name = a.name
	JOIN friedrich_customer_price_levels c ON c.customer_id = a.id
	JOIN vendor_pricing_classes vpc ON vpc.name = c.price_level::VARCHAR
	WHERE vc.vendor_id = 'friedrich';

-- TRIGGERS
-- vendor consistency
CREATE OR REPLACE FUNCTION vendor_pricing_consistency_fn()
RETURNS TRIGGER AS $$
DECLARE
    vp_vendor_id VARCHAR;
    vpc_vendor_id VARCHAR;
    vc_vendor_id VARCHAR;
BEGIN
    -- Get the vendor_id of the product
    SELECT vendor_id INTO vp_vendor_id
	FROM vendor_products
	WHERE vendor_products.id = NEW.product_id;
    
    -- Get the vendor_id of the pricing class
    SELECT vendor_id INTO vpc_vendor_id
	FROM vendor_pricing_classes
	WHERE vendor_pricing_classes.id = NEW.pricing_class_id;

    -- Get the vendor_id of the vendor customer
    SELECT vendor_id INTO vc_vendor_id
	FROM vendor_customers
	WHERE vendor_customers.id = NEW.vendor_customer_id;
    
    -- Ensure they match
    IF NOT (vp_vendor_id <=> vpc_vendor_id AND vp_vendor_id <=> vc_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between product, customer, and/or pricing class';
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_pricing_consistency
BEFORE INSERT ON vendor_pricing_by_class
FOR EACH ROW
EXECUTE FUNCTION vendor_pricing_consistency_fn();

-- CREATE TRIGGER ensure_vendor_consistency_product_classes
-- BEFORE INSERT ON vendor_pricing
-- FOR EACH ROW
-- BEGIN
--     DECLARE pc_vendor_id VARCHAR;
--     DECLARE p_vendor_id VARCHAR;
    
--     -- Get the vendor_id of the product
--     SELECT vendor_id INTO p_vendor_id FROM vendor_products WHERE vendor_products.id = NEW.product_id;
    
--     -- Get the vendor_id of the product class
--     SELECT vendor_id INTO pc_vendor_id FROM vendor_product_classes WHERE vendor_product_classes.id = NEW.product_class_id;

    
--     -- Ensure they match
--     IF p_vendor_id != pc_vendor_id THEN
--         SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Vendor mismatch between product and product class';
--     END IF;
-- END;

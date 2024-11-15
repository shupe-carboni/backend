-- NEW TABLES
-- vendors
-- deleted_at column will be added after data transfer for vendors
CREATE TABLE vendors (
	name VARCHAR,
	headquarters VARCHAR,
	description TEXT,
	phone BIGINT,
	logo_path VARCHAR,
	id VARCHAR PRIMARY KEY);

CREATE TABLE vendors_attrs (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	deleted_at TIMESTAMP);
-- customers
CREATE TABLE vendor_customers (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	name VARCHAR,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_customer_attrs (
	id SERIAL PRIMARY KEY,
	vendor_customer_id INT REFERENCES vendor_customers(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	deleted_at TIMESTAMP,
	UNIQUE (vendor_customer_id, attr, type, value));

-- products
CREATE TABLE vendor_products (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	vendor_product_identifier VARCHAR,
	vendor_product_description VARCHAR,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_product_classes (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	name VARCHAR,
	rank INT,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_product_to_class_mapping (
	id SERIAL PRIMARY KEY,
	product_class_id INT REFERENCES vendor_product_classes(id),
	product_id INT REFERENCES vendor_products(id),
	deleted_at TIMESTAMP);
CREATE TABLE vendor_product_attrs (
	id SERIAL PRIMARY KEY,
	vendor_product_id INT REFERENCES vendor_products(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	deleted_at TIMESTAMP);

-- pricing
CREATE TABLE vendor_pricing_classes (
	id SERIAL PRIMARY KEY,
	vendor_id VARCHAR REFERENCES vendors(id),
	name VARCHAR,
	deleted_at TIMESTAMP,
	UNIQUE(vendor_id, name));
CREATE TABLE vendor_pricing_by_class (
	id SERIAL PRIMARY KEY,
	pricing_class_id INT REFERENCES vendor_pricing_classes(id),
	product_id INT REFERENCES vendor_products(id),
	price INT,
	effective_date TIMESTAMP DEFAULT CURRENT_DATE,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_pricing_by_customer (
	id SERIAL PRIMARY KEY,
	product_id INT REFERENCES vendor_products(id),
	pricing_class_id INT REFERENCES vendor_pricing_classes(id),
	vendor_customer_id INT REFERENCES vendor_customers(id),
	use_as_override BOOLEAN DEFAULT false,
	price INT,
	effective_date TIMESTAMP DEFAULT CURRENT_DATE,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_product_class_discounts (
	id SERIAL PRIMARY KEY,
	product_class_id INT REFERENCES vendor_product_classes(id),
	vendor_customer_id INT REFERENCES vendor_customers(id),
	discount FLOAT,
	effective_date TIMESTAMP DEFAULT CURRENT_DATE,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_product_discounts (
	id SERIAL PRIMARY KEY,
	product_id INT REFERENCES vendor_products(id),
	vendor_customer_id INT REFERENCES vendor_customers(id),
	discount FLOAT,
	effective_date TIMESTAMP DEFAULT CURRENT_DATE,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_customer_pricing_classes (
	id SERIAL PRIMARY KEY,
	pricing_class_id INT REFERENCES vendor_pricing_classes(id),
	vendor_customer_id INT REFERENCES vendor_customers(id),
	deleted_at TIMESTAMP);
CREATE TABLE vendor_pricing_by_customer_attrs (
	id SERIAL PRIMARY KEY,
	pricing_by_customer_id INT REFERENCES vendor_pricing_by_customer(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	deleted_at TIMESTAMP,
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
	plans_doc VARCHAR,
	deleted_at TIMESTAMP);
CREATE TABLE vendor_quotes_attrs (
	id SERIAL PRIMARY KEY,
	vendor_quotes_id INT REFERENCES vendor_quotes(id),
	attr VARCHAR,
	type VARCHAR,
	value VARCHAR,
	deleted_at TIMESTAMP,
	UNIQUE (vendor_quotes_id, attr, type, value));
CREATE TABLE vendor_quote_products (
	id SERIAL PRIMARY KEY,
	vendor_quotes_id INT REFERENCES vendor_quotes(id),
	product_id INT REFERENCES vendor_products(id),
	tag VARCHAR,
	competitor_model VARCHAR,
	qty INT,
	price INT,
	deleted_at TIMESTAMP);

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
	customer_location_id INT REFERENCES sca_customer_locations(id),
	deleted_at TIMESTAMP);

-- admin table
CREATE TABLE customer_admin_map (
	id SERIAL PRIMARY KEY,
	user_id INT REFERENCES sca_users(id),
	customer_id INT REFERENCES sca_customers(id));

-- changelogs
-- vendor customer attributes
CREATE TABLE vendor_customer_attrs_changelog (
	id SERIAL PRIMARY KEY,
	attr_id INT REFERENCES vendor_customer_attrs(id),
	value VARCHAR,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor customer pricing classes changelog
CREATE TABLE vendor_customer_pricing_classes_changelog (
	id SERIAL PRIMARY KEY,
	pricing_class_id INT REFERENCES vendor_pricing_classes(id),
	vendor_customer_id INT REFERENCES vendor_customers(id),
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor customers changelog
CREATE TABLE vendor_customers_changelog (
	id SERIAL PRIMARY KEY,
	vendor_customer_id INT REFERENCES vendor_customers(id),
	name VARCHAR,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
	
-- vendor pricing by class changelog
CREATE TABLE vendor_pricing_by_class_changelog (
	id SERIAL PRIMARY KEY,
	vendor_pricing_by_class_id INT REFERENCES vendor_pricing_by_class(id),
	price INT,
	effective_date TIMESTAMP,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor pricing by customer changelog
CREATE TABLE vendor_pricing_by_customer_changelog (
	id SERIAL PRIMARY KEY,
	vendor_pricing_by_customer_id INT REFERENCES vendor_pricing_by_customer(id),
	price INT,
	effective_date TIMESTAMP,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor product class discount changelog
CREATE TABLE vendor_product_class_discounts_changelog (
	id SERIAL PRIMARY KEY,
	vendor_product_class_discounts_id INT REFERENCES vendor_product_class_discounts(id),
	discount FLOAT,
	effective_date TIMESTAMP,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor product discount changelog
CREATE TABLE vendor_product_discounts_changelog (
	id SERIAL PRIMARY KEY,
	vendor_product_discounts_id INT REFERENCES vendor_product_discounts(id),
	discount FLOAT,
	effective_date TIMESTAMP,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor quote products changelog
CREATE TABLE vendor_quote_products_changelog (
	id SERIAL PRIMARY KEY,
	vendor_quote_products_id INT REFERENCES vendor_quote_products(id),
	qty INT,
	price INT,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor quotes changelog
CREATE TABLE vendor_quotes_changelog (
	id SERIAL PRIMARY KEY,
	vendor_quotes_id INT REFERENCES vendor_quotes(id),
	status stage,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- vendor attrs changelog
CREATE TABLE vendors_attrs_changelog (
	id SERIAL PRIMARY KEY,
	attr_id INT REFERENCES vendors_attrs(id),
	value VARCHAR,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- TRIGGERS
-- VENDOR CONSISTENCY

-- pricing by customer
CREATE OR REPLACE FUNCTION vendor_pricing_by_customer_consistency_fn()
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
    IF NOT (vp_vendor_id IS NOT DISTINCT FROM vpc_vendor_id AND vp_vendor_id IS NOT DISTINCT FROM vc_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between product, customer, and/or pricing class';
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_pricing_by_customer_consistency
BEFORE INSERT ON vendor_pricing_by_customer
FOR EACH ROW
EXECUTE FUNCTION vendor_pricing_by_customer_consistency_fn();

-- pricing by class
CREATE OR REPLACE FUNCTION vendor_pricing_by_class_consistency_fn()
RETURNS TRIGGER AS $$
DECLARE
    vp_vendor_id VARCHAR;
    vpc_vendor_id VARCHAR;
BEGIN
    -- Get the vendor_id of the product
    SELECT vendor_id INTO vp_vendor_id
	FROM vendor_products
	WHERE vendor_products.id = NEW.product_id;
    
    -- Get the vendor_id of the pricing class
    SELECT vendor_id INTO vpc_vendor_id
	FROM vendor_pricing_classes
	WHERE vendor_pricing_classes.id = NEW.pricing_class_id;
    
    -- Ensure they match
    IF NOT (vp_vendor_id IS NOT DISTINCT FROM vpc_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between product and pricing class';
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_pricing_by_class_consistency
BEFORE INSERT ON vendor_pricing_by_class
FOR EACH ROW
EXECUTE FUNCTION vendor_pricing_by_class_consistency_fn();

-- customer pricing classes
CREATE OR REPLACE FUNCTION vendor_customer_pricing_classes_consistency_fn()
RETURNS TRIGGER AS $$
DECLARE
    vc_vendor_id VARCHAR;
    vpc_vendor_id VARCHAR;
BEGIN
    -- customer
    SELECT vendor_id INTO vc_vendor_id
	FROM vendor_customers
	WHERE vendor_customers.id = NEW.vendor_customer_id;
    
    -- pricing class
    SELECT vendor_id INTO vpc_vendor_id
	FROM vendor_pricing_classes
	WHERE vendor_pricing_classes.id = NEW.pricing_class_id;
    
    -- Ensure they match
    IF NOT (vc_vendor_id IS NOT DISTINCT FROM vpc_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between pricing class and customer. vendor_customer=% vendor_pricing_class=%', vc_vendor_id, vpc_vendor_id;
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_customer_pricing_classes_consistency
BEFORE INSERT ON vendor_customer_pricing_classes
FOR EACH ROW
EXECUTE FUNCTION vendor_customer_pricing_classes_consistency_fn();

-- product class discounts
CREATE OR REPLACE FUNCTION vendor_product_class_discounts_consistency_fn()
RETURNS TRIGGER AS $$
DECLARE
    vc_vendor_id VARCHAR;
    vpc_vendor_id VARCHAR;
BEGIN
    -- customer
    SELECT vendor_id INTO vc_vendor_id
	FROM vendor_customers
	WHERE vendor_customers.id = NEW.vendor_customer_id;
    
    -- product class
    SELECT vendor_id INTO vpc_vendor_id
	FROM vendor_product_classes
	WHERE vendor_product_classes.id = NEW.product_class_id;
    
    -- Ensure they match
    IF NOT (vc_vendor_id IS NOT DISTINCT FROM vpc_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between product class and customer';
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_product_class_discounts_consistency
BEFORE INSERT ON vendor_product_class_discounts
FOR EACH ROW
EXECUTE FUNCTION vendor_product_class_discounts_consistency_fn();

-- product class discounts
CREATE OR REPLACE FUNCTION vendor_product_discounts_consistency_fn()
RETURNS TRIGGER AS $$
DECLARE
    vc_vendor_id VARCHAR;
    vp_vendor_id VARCHAR;
BEGIN
    -- customer
    SELECT vendor_id INTO vc_vendor_id
	FROM vendor_customers
	WHERE vendor_customers.id = NEW.vendor_customer_id;
    
    -- product
    SELECT vendor_id INTO vp_vendor_id
	FROM vendor_products
	WHERE vendor_products.id = NEW.product_id;
    
    -- Ensure they match
    IF NOT (vc_vendor_id IS NOT DISTINCT FROM vp_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between product and customer';
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_product_discounts_consistency
BEFORE INSERT ON vendor_product_discounts
FOR EACH ROW
EXECUTE FUNCTION vendor_product_discounts_consistency_fn();

-- product to class mapping
CREATE OR REPLACE FUNCTION vendor_product_to_class_mapping_consistency_fn()
RETURNS TRIGGER AS $$
DECLARE
    vp_vendor_id VARCHAR;
    vpc_vendor_id VARCHAR;
BEGIN
    -- product
    SELECT vendor_id INTO vp_vendor_id
	FROM vendor_products
	WHERE vendor_products.id = NEW.product_id;
    
    -- product class
    SELECT vendor_id INTO vpc_vendor_id
	FROM vendor_product_classes
	WHERE vendor_product_classes.id = NEW.product_class_id;
    
    -- Ensure they match
    IF NOT (vp_vendor_id IS NOT DISTINCT FROM vpc_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between product class and product';
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_product_to_class_mapping_consistency
BEFORE INSERT ON vendor_product_to_class_mapping
FOR EACH ROW
EXECUTE FUNCTION vendor_product_to_class_mapping_consistency_fn();

-- quote products
CREATE OR REPLACE FUNCTION vendor_quote_product_consistency_fn()
RETURNS TRIGGER AS $$
DECLARE
    vp_vendor_id VARCHAR;
    vc_vendor_id VARCHAR;
BEGIN
    -- product
    SELECT vendor_id INTO vp_vendor_id
	FROM vendor_products
	WHERE vendor_products.id = NEW.product_id;
    
    -- customer
    SELECT vendor_id INTO vc_vendor_id
	FROM vendor_customers
	WHERE EXISTS (
		SELECT 1
		FROM vendor_quotes
		WHERE vendor_quotes.id = NEW.vendor_quotes_id
		AND vendor_quotes.vendor_customer_id = vendor_customers.id
	);
    
    -- Ensure they match
	
    IF NEW.product_id IS NOT NULL AND NOT (vp_vendor_id IS NOT DISTINCT FROM vc_vendor_id) THEN
        RAISE EXCEPTION 'Vendor mismatch between product and customer quoted';
    END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_quote_product_consistency
BEFORE INSERT ON vendor_quote_products
FOR EACH ROW
EXECUTE FUNCTION vendor_quote_product_consistency_fn();

-- CHANGELOGS
-- vendor customer attributes
-- new values
CREATE OR REPLACE FUNCTION vendor_customer_attrs_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_customer_attrs_changelog (attr_id, value)
	VALUES (NEW.id, NEW.value);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_customer_attrs_changelog_insert
AFTER INSERT ON vendor_customer_attrs
FOR EACH ROW
EXECUTE FUNCTION vendor_customer_attrs_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_customer_attrs_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.value != NEW.value THEN
		INSERT INTO vendor_customer_attrs_changelog (attr_id, value)
		VALUES (OLD.id, NEW.value);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_customer_attrs_changelog_update
BEFORE UPDATE ON vendor_customer_attrs
FOR EACH ROW
EXECUTE FUNCTION vendor_customer_attrs_changelog_update_fn();

-- vendor customer pricing classes
-- new values
CREATE OR REPLACE FUNCTION vendor_customer_pricing_classes_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_customer_pricing_classes_changelog (pricing_class_id, vendor_customer_id)
	VALUES (NEW.pricing_class_id, NEW.vendor_customer_id);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_customer_pricing_classes_changelog_insert
AFTER INSERT ON vendor_customer_pricing_classes
FOR EACH ROW
EXECUTE FUNCTION vendor_customer_pricing_classes_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_customer_pricing_classes_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.pricing_class_id != NEW.pricing_class_id THEN
		INSERT INTO vendor_customer_pricing_classes_changelog (pricing_class_id, vendor_customer_id)
		VALUES (OLD.pricing_class_id, NEW.vendor_customer_id);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_customer_pricing_classes_changelog_update
BEFORE UPDATE ON vendor_customer_pricing_classes
FOR EACH ROW
EXECUTE FUNCTION vendor_customer_pricing_classes_changelog_update_fn();

-- vendor customers
-- new values
CREATE OR REPLACE FUNCTION vendor_customers_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_customers_changelog (vendor_customer_id, name)
	VALUES (NEW.id, NEW.name);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_customers_changelog_insert
AFTER INSERT ON vendor_customers
FOR EACH ROW
EXECUTE FUNCTION vendor_customers_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_customers_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.name != NEW.name THEN
		INSERT INTO vendor_customers_changelog (vendor_customer_id, name)
		VALUES (OLD.id, NEW.name);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_customers_changelog_update
BEFORE UPDATE ON vendor_customers
FOR EACH ROW
EXECUTE FUNCTION vendor_customers_changelog_update_fn();

-- vendor pricing by class
-- new values
CREATE OR REPLACE FUNCTION vendor_pricing_by_class_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_pricing_by_class_changelog (vendor_pricing_by_class_id, price, effective_date)
	VALUES (NEW.id, NEW.price, NEW.effective_date);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_pricing_by_class_changelog_insert
AFTER INSERT ON vendor_pricing_by_class
FOR EACH ROW
EXECUTE FUNCTION vendor_pricing_by_class_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_pricing_by_class_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.price != NEW.price OR OLD.effective_date != NEW.effective_date THEN
		INSERT INTO vendor_pricing_by_class_changelog (vendor_pricing_by_class_id, price, effective_date)
		VALUES (OLD.id, NEW.price, NEW.effective_date);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_pricing_by_class_changelog_update
BEFORE UPDATE OF price, effective_date ON vendor_pricing_by_class
FOR EACH ROW
EXECUTE FUNCTION vendor_pricing_by_class_changelog_update_fn();

-- vendor pricing by customer
-- new values
CREATE OR REPLACE FUNCTION vendor_pricing_by_customer_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_pricing_by_customer_changelog (vendor_pricing_by_customer_id, price, effective_date)
	VALUES (NEW.id, NEW.price, NEW.effective_date);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_pricing_by_customer_changelog_insert
AFTER INSERT ON vendor_pricing_by_customer
FOR EACH ROW
EXECUTE FUNCTION vendor_pricing_by_customer_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_pricing_by_customer_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.price != NEW.price OR OLD.effective_date != NEW.effective_date THEN
		INSERT INTO vendor_pricing_by_customer_changelog (vendor_pricing_by_customer_id, price, effective_date)
		VALUES (OLD.id, NEW.price, NEW.effective_date);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_pricing_by_customer_changelog_update
BEFORE UPDATE OF price, effective_date ON vendor_pricing_by_customer
FOR EACH ROW
EXECUTE FUNCTION vendor_pricing_by_customer_changelog_update_fn();

-- vendor product class discount
-- new values
CREATE OR REPLACE FUNCTION vendor_product_class_discounts_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_product_class_discounts_changelog (vendor_product_class_discounts_id, discount, effective_date)
	VALUES (NEW.id, NEW.discount, NEW.effective_date);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_product_class_discounts_changelog_insert
AFTER INSERT ON vendor_product_class_discounts
FOR EACH ROW
EXECUTE FUNCTION vendor_product_class_discounts_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_product_class_discounts_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.discount != NEW.discount OR OLD.effective_date != NEW.effective_date THEN
		INSERT INTO vendor_product_class_discounts_changelog (vendor_product_class_discounts_id, discount, effective_date)
		VALUES (OLD.id, NEW.discount, NEW.effective_date);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_product_class_discounts_changelog_update
BEFORE UPDATE OF discount, effective_date ON vendor_product_class_discounts
FOR EACH ROW
EXECUTE FUNCTION vendor_product_class_discounts_changelog_update_fn();

-- vendor product discount
-- new values
CREATE OR REPLACE FUNCTION vendor_product_discounts_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_product_discounts_changelog (vendor_product_discounts_id, discount, effective_date)
	VALUES (NEW.id, NEW.discount, NEW.effective_date);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_product_discounts_changelog_insert
AFTER INSERT ON vendor_product_discounts
FOR EACH ROW
EXECUTE FUNCTION vendor_product_discounts_changelog_insert_fn();

-- updates
CREATE OR REPLACE FUNCTION vendor_product_discounts_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF OLD.discount != NEW.discount OR OLD.effective_date != NEW.effective_date THEN
		INSERT INTO vendor_product_discounts_changelog (vendor_product_discounts_id, discount, effective_date)
		VALUES (OLD.id, NEW.discount, NEW.effective_date);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_product_discounts_changelog_update
BEFORE UPDATE OF discount, effective_date ON vendor_product_discounts
FOR EACH ROW
EXECUTE FUNCTION vendor_product_discounts_changelog_update_fn();

-- vendor quote products
-- new values
CREATE OR REPLACE FUNCTION vendor_quote_products_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_quote_products_changelog (vendor_quote_products_id, qty, price)
	VALUES (NEW.id, NEW.qty, NEW.price);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_quote_products_changelog_insert
AFTER INSERT ON vendor_quote_products
FOR EACH ROW
EXECUTE FUNCTION vendor_quote_products_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_quote_products_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF (OLD.qty != NEW.qty OR OLD.price != NEW.price) THEN
		INSERT INTO vendor_quote_products_changelog (vendor_quote_products_id, qty, price)
		VALUES (OLD.id, NEW.qty, NEW.price);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_quote_products_changelog_update
BEFORE UPDATE ON vendor_quote_products
FOR EACH ROW
EXECUTE FUNCTION vendor_quote_products_changelog_update_fn();

-- vendor quotes
-- new values
CREATE OR REPLACE FUNCTION vendor_quotes_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendor_quotes_changelog (vendor_quotes_id, status)
	VALUES (NEW.id, NEW.status);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_quotes_changelog_insert
AFTER INSERT ON vendor_quotes
FOR EACH ROW
EXECUTE FUNCTION vendor_quotes_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendor_quotes_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF NEW.status != OLD.status THEN
		INSERT INTO vendor_quotes_changelog (vendor_quotes_id, status)
		VALUES (OLD.id, NEW.status);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendor_quotes_changelog_update
BEFORE UPDATE ON vendor_quotes
FOR EACH ROW
EXECUTE FUNCTION vendor_quotes_changelog_update_fn();

-- vendor attrs
-- new values
CREATE OR REPLACE FUNCTION vendors_attrs_changelog_insert_fn()
RETURNS TRIGGER AS $$
BEGIN
	INSERT INTO vendors_attrs_changelog (attr_id, value)
	VALUES (NEW.id, NEW.value);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendors_attrs_changelog_insert
AFTER INSERT ON vendors_attrs
FOR EACH ROW
EXECUTE FUNCTION vendors_attrs_changelog_insert_fn();
-- updates
CREATE OR REPLACE FUNCTION vendors_attrs_changelog_update_fn()
RETURNS TRIGGER AS $$
BEGIN
	IF NEW.value != OLD.value THEN
		INSERT INTO vendors_attrs_changelog (attr_id, value)
		VALUES (OLD.id, NEW.value);
	END IF;
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER vendors_attrs_changelog_update
BEFORE UPDATE ON vendors_attrs
FOR EACH ROW
EXECUTE FUNCTION vendors_attrs_changelog_update_fn();


-- MOVE DATA
-- vendors
INSERT INTO vendors
SELECT * FROM sca_vendors;

INSERT INTO vendors
VALUES (
	'Hardcast',
	'900 Hensley Lane, Wylie, Texas 75098',
	'Duct Sealants and Adhesives, DynAir Airflow Hardware and Accessories, and the Nexus 4-Bolt Flange Closure System.',
	8774954822,
	'vendors/hardcast/logo/hardcast-logo.png',
	'hardcast');

ALTER TABLE vendors ADD deleted_at TIMESTAMP;

INSERT INTO customer_admin_map (user_id, customer_id)
VALUES (1,181);

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
		'NUMBER' AS type, friedrich_acct_number::VARCHAR AS value
	FROM friedrich_customers a
	JOIN vendor_customers b
	ON b.name = a.name
	AND b.vendor_id = 'friedrich'
	WHERE friedrich_acct_number IS NOT NULL;

-- customer location mapping
-- adp
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
	ON d.customer_location_id = c.id
	WHERE ppf IS NOT NULL;

INSERT INTO vendor_customer_attrs (vendor_customer_id, attr, type, value)
	SELECT DISTINCT d.vendor_customer_id, 'terms', 'STRING', terms
	FROM adp_customer_terms AS a
	JOIN sca_customers AS b
	ON b.id = a.sca_id
	JOIN sca_customer_locations AS c
	ON c.customer_id = b.id
	JOIN customer_location_mapping AS d
	ON d.customer_location_id = c.id
	WHERE terms IS NOT NULL;

-- products
-- adp
INSERT INTO vendor_products (vendor_id, vendor_product_identifier)
	SELECT DISTINCT 'adp', model_number
	FROM adp_coil_programs;
INSERT INTO vendor_products (vendor_id, vendor_product_identifier)
	SELECT DISTINCT 'adp', model_number
	FROM adp_ah_programs;
INSERT INTO vendor_products (vendor_id, vendor_product_identifier)
	SELECT DISTINCT 'adp', model
	FROM adp_snps
	WHERE NOT EXISTS (
		SELECT 1
		FROM vendor_products
		WHERE vendor_products.vendor_product_identifier = adp_snps.model
		AND vendor_products.vendor_id = 'adp'
	);

INSERT INTO vendor_products (vendor_id, vendor_product_identifier, vendor_product_description)
	SELECT DISTINCT 'adp', adppp.part_number::VARCHAR, adppp.description
	FROM adp_pricing_parts AS adppp;
-- friedrich
INSERT INTO vendor_products (vendor_id, vendor_product_identifier, vendor_product_description)
	SELECT DISTINCT 'friedrich', f.model_number, f.description
	FROM friedrich_products f;
-- hardcast
INSERT INTO vendor_products (vendor_id, vendor_product_identifier, vendor_product_description)
	SELECT DISTINCT 'hardcast', hc.product_number::VARCHAR, hc.description
	FROM hardcast_products hc;

-- hardcast attrs
INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id, 'code', 'STRING', code
	FROM hardcast_products a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.product_number::VARCHAR
	AND b.vendor_product_description = a.description
	WHERE b.vendor_id = 'hardcast';

INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id, unnest(array['upc','freight_class','weight','case_qty']),
		'NUMBER', unnest(array[upc, freight_class, weight, case_qty])
	FROM hardcast_products a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.product_number::VARCHAR
	AND b.vendor_product_description = a.description
	WHERE b.vendor_id = 'hardcast';

INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id, 'haz_mat', 'BOOLEAN', haz_mat
	FROM hardcast_products a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.product_number::VARCHAR
	AND b.vendor_product_description = a.description
	WHERE b.vendor_id = 'hardcast';

INSERT INTO vendor_product_attrs (vendor_product_id, attr, type, value)
	SELECT DISTINCT b.id, 'stock', 'ARRAY', array_to_string(stock, ',')
	FROM hardcast_products a
	JOIN vendor_products b
	ON b.vendor_product_identifier = a.product_number::VARCHAR
	AND b.vendor_product_description = a.description
	WHERE b.vendor_id = 'hardcast';

-- adp attrs
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

-- adp parts attrs
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

-- migrate adp snp discounts to vendor product discounts
INSERT INTO vendor_product_discounts (product_id, vendor_customer_id, discount)
	SELECT p.id, vc.id, adp.discount
	FROM (
		SELECT snp.customer_id, snp.model,
			ROUND((1-(snp.price::NUMERIC / (vpc.price/100)::NUMERIC))*100, 2) AS discount
		FROM adp_snps AS snp
		JOIN vendor_products AS p
		ON p.vendor_product_identifier = snp.model
		JOIN vendor_pricing_by_class AS vpc
		ON vpc.product_id = p.id
		JOIN vendor_pricing_classes AS classes
		ON classes.id = vpc.pricing_class_id
		WHERE classes.name = 'ZERO_DISCOUNT'
		AND classes.vendor_id = 'adp'
	) as adp
	JOIN vendor_products AS p
	ON p.vendor_product_identifier = adp.model
	JOIN adp_customers AS ac
	ON ac.id = adp.customer_id
	JOIN vendor_customers AS vc
	ON vc.name = ac.adp_alias
	WHERE p.vendor_id = 'adp'
	AND vc.vendor_id = 'adp';

-- price classes
INSERT INTO vendor_pricing_classes (vendor_id, name)
	VALUES ('adp', 'ZERO_DISCOUNT'),
		   ('adp', 'STRATEGY_PRICING'),
		   ('adp', 'PREFERRED_PARTS'),
		   ('adp', 'STANDARD_PARTS'),
		   ('friedrich', 'STANDARD'),
		   ('friedrich', 'STOCKING'),
		   ('friedrich', 'NON_STOCKING'),
		   ('hardcast', 'STANDARD');
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
-- hardcast
INSERT INTO vendor_pricing_by_class (pricing_class_id, product_id, price)
	SELECT DISTINCT vpc.id, p.id, (a.case_price*100)::INT
	FROM hardcast_products a
	JOIN vendor_products p ON p.vendor_product_identifier = a.product_number::VARCHAR
	JOIN vendors v ON v.id = p.vendor_id
	JOIN vendor_pricing_classes vpc ON vpc.vendor_id = v.id
	WHERE v.id = 'hardcast'
	AND vpc.name = 'STANDARD';
	
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
-- friedrich special pricing
INSERT INTO vendor_pricing_by_customer (product_id, pricing_class_id, vendor_customer_id, use_as_override, price)
	SELECT DISTINCT p.id, pc.id, vc.id, true, (price*100)::INT
	FROM friedrich_pricing_special a
	JOIN friedrich_customers fc ON fc.id = a.customer_id
	JOIN vendor_customers vc ON vc.name = fc.name
	JOIN friedrich_products b ON a.model_number_id = b.id
	JOIN vendor_products p ON p.vendor_product_identifier = b.model_number
	JOIN vendors v ON v.id = p.vendor_id
	JOIN vendor_pricing_classes pc ON pc.vendor_id = v.id 
	WHERE v.id = 'friedrich'
	AND pc.name = 'STOCKING';
-- customer-specific model numbers associated with products
INSERT INTO vendor_pricing_by_customer_attrs (pricing_by_customer_id, attr, type, value)
	SELECT DISTINCT vpbc.id, 'customer_model_number', 'STRING', customer_model_number
	FROM friedrich_pricing_special a
	JOIN friedrich_customers fc ON fc.id = a.customer_id
	JOIN vendor_customers vc ON vc.name = fc.name
	JOIN friedrich_products b ON a.model_number_id = b.id
	JOIN vendor_products p ON p.vendor_product_identifier = b.model_number
	JOIN vendors v ON v.id = p.vendor_id
	JOIN vendor_pricing_classes pc ON pc.vendor_id = v.id
	JOIN vendor_pricing_by_customer vpbc ON vpbc.product_id = p.id AND vpbc.pricing_class_id = pc.id AND vpbc.vendor_customer_id = vc.id
	WHERE customer_model_number IS NOT NULL;

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
	AND vpc.vendor_id = vc.vendor_id
	WHERE vc.vendor_id = 'friedrich';

-- vendor info to attributes
INSERT INTO vendors_attrs (vendor_id, attr, type, value)
	SELECT DISTINCT vendor_id, category, 'STRING', content
	FROM sca_vendors_info
	WHERE content IS NOT NULL;

DELETE FROM vendor_product_attrs
WHERE value IS NULL;

DELETE FROM vendor_customer_attrs
WHERE value IS NULL;

DELETE FROM vendor_quotes_attrs
WHERE value IS NULL;

DELETE FROM vendors_attrs
WHERE value IS NULL;
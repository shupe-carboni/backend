CREATE TEMPORARY TABLE customer_price_temp (
    model varchar,
    customer varchar,
    customer_id int,
    price real);
CREATE TEMPORARY TABLE class_price_temp (
    model varchar,
    price_class varchar,
    price_class_id int,
    price real);
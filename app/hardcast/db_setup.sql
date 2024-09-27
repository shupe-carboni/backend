CREATE TABLE IF NOT EXISTS hardcast_confirmations (
    id SERIAL PRIMARY KEY,
    order_confirmation_number INT NOT NULL,
    order_confirmation_date TIMESTAMP DEFAULT CURRENT_DATE NOT NULL,
    purchase_order_number VARCHAR NOT NULL,
    customer_number INT NOT NULL,
    sold_to_customer_name VARCHAR NOT NULL,
    sold_to_customer_address VARCHAR NOT NULL,
    ship_to_customer_name VARCHAR NOT NULL,
    ship_to_customer_address VARCHAR NOT NULL,
    terms_of_payment VARCHAR,
    terms_of_delivery VARCHAR,
    subtotal INT NOT NULL,
    state_tax INT NOT NULL,
    county_tax INT NOT NULL,
    total_amount INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS hardcast_confirmation_products (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    item_sequence_number INT NOT NULL,
    material_number VARCHAR NOT NULL,
    material_description TEXT NOT NULL,
    ship_from VARCHAR NOT NULL,
    delivery_date TIMESTAMP DEFAULT CURRENT_DATE,
    quantity FLOAT NOT NULL,
    unit_of_measure VARCHAR NOT NULL,
    unit_price INT NOT NULL,
    total INT NOT NULL,
    FOREIGN KEY(order_id) REFERENCES hardcast_confirmations(id)
);

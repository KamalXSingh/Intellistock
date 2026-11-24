CREATE TABLE products(
id SERIAL PRIMARY KEY,
name VARCHAR(50) NOT NULL,
category VARCHAR(50) NOT NULL,
price Numeric(10,2) NOT NULL,
quantity INTEGER NOT NULL DEFAULT 0,
sku VARCHAR(50) UNIQUE NOT NULL,
description TEXT,
is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO products(name, category, price, quantity,sku, description,is_active)
('Wireless Headphones', 'Electronics', 2499.00, 50, 'ELEC-101', 'Bluetooth headphones'),
('Mechanical Keyboard', 'Electronics', 3999.00, 30, 'ELEC-102', 'RGB mechanical keyboard'),
('Gaming Mouse', 'Electronics', 1499.00, 100, 'ELEC-103', 'Wireless gaming mouse');


SELECT * FROM products
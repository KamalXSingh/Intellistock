-- SELECT * FROM products;
-- SELECT * FROM suppliers;
-- SELECT * FROM product_suppliers

-- SELECT name FROM products;
-- SELECT * FROM products WHERE quantity < 60;

-- UPDATE products 
-- SET supplier_id = 1
-- WHERE id IN (1,2);

-- UPDATE products
-- SET supplier_id = 2
-- WHERE id = 3;

-- SELECT p.name from products,
-- s.name from suppliers

-- SELECT p.name as product_name,
-- s.name as seller_name
-- FROM products p
-- JOIN product_suppliers ps
-- ON p.id=ps.product_id
-- JOIN suppliers s
-- ON s.id = ps.supplier_id

-- SELECT p.name as product_name,
-- s.name as seller_name,
-- p.price as product_price
-- FROM products p
-- JOIN product_suppliers ps
-- ON p.id=ps.product_id
-- JOIN suppliers s
-- ON s.id = ps.supplier_id
-- ORDER BY p.price desc;



-- Check existing product categories
-- SELECT DISTINCT category
-- FROM products
-- ORDER BY category;

-- Check categories in the categories table
-- SELECT id, name
-- FROM categories
-- ORDER BY id;


-- ALTER TABLE products
-- ADD COLUMN category_id INTEGER;

-- UPDATE products
-- SET category_id = (
--     SELECT id
--     FROM categories
--     WHERE categories.name = products.category
-- );

-- ALTER TABLE products
-- ADD CONSTRAINT fk_products_category
-- FOREIGN KEY (category_id)
-- REFERENCES categories(id);


-- SELECT
--     p.id,
--     p.name,
--     w.name AS warehouse,
--     ws.quantity
-- FROM products p
-- LEFT JOIN warehouse_stock ws ON p.id = ws.product_id
-- LEFT JOIN warehouses w ON ws.warehouse_id = w.id
-- ORDER BY p.id;

-- SELECT * FROM warehouses;

-- SELECT * from products;

-- select * from stock_movements
select * from warehouse_stock

-- SELECT 
--     con.conname AS constraint_name,
--     con.contype AS constraint_type,
--     pg_get_constraintdef(con.oid) AS definition
-- FROM pg_catalog.pg_constraint con
-- INNER JOIN pg_catalog.pg_class rel ON rel.oid = con.conrelid
-- INNER JOIN pg_catalog.pg_namespace nsp ON nsp.oid = con.connamespace
-- WHERE nsp.nspname = 'public'
--   AND rel.relname = 'stock_movements';

-- select * from warehouse_stock;



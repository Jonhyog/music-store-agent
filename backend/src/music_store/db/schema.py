"""The store database definition: DDL and the CSV columns loaded into each table."""

SCHEMA = """
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER REFERENCES categories (category_id),
    name TEXT NOT NULL,
    price_brl REAL NOT NULL,
    description TEXT,
    stock_quantity INTEGER NOT NULL,
    status TEXT,
    specs TEXT CHECK (specs IS NULL OR json_valid(specs)),
    created_at DATE
);
CREATE TABLE promotions (
    promotion_id INTEGER PRIMARY KEY,
    product_id INTEGER REFERENCES products (product_id),
    discount_percent INTEGER CHECK (discount_percent BETWEEN 0 AND 100),
    description TEXT,
    is_active INTEGER CHECK (is_active IN (0, 1))
);
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    city TEXT
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers (customer_id),
    order_date DATE,
    status TEXT,
    total_brl REAL,
    payment_method TEXT,
    tracking_code TEXT,
    estimated_delivery DATE,
    notes TEXT
);
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders (order_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
"""

# Load order respects foreign keys. Columns are listed explicitly so CSV column order is irrelevant.
TABLES: dict[str, list[str]] = {
    "categories": ["category_id", "name", "description"],
    "customers": ["customer_id", "name", "phone", "email", "city"],
    "products": [
        "product_id",
        "category_id",
        "name",
        "price_brl",
        "description",
        "stock_quantity",
        "status",
        "specs",
        "created_at",
    ],
    "promotions": ["promotion_id", "product_id", "discount_percent", "description", "is_active"],
    "orders": [
        "order_id",
        "customer_id",
        "order_date",
        "status",
        "total_brl",
        "payment_method",
        "tracking_code",
        "estimated_delivery",
        "notes",
    ],
    "order_items": ["order_id", "product_id", "quantity"],
}

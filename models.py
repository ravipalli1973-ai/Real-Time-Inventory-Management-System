import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "data", "inventory.db")


def get_connection():
    """Returns an active SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def add_product(product_name, category, price, quantity, supplier):
    """Inserts a new product into the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (product_name, category, price, quantity, supplier)
            VALUES (?, ?, ?, ?, ?)
        """, (product_name.strip(), category.strip(), float(price), int(quantity), supplier.strip()))
        return cursor.lastrowid


def get_total_products():
    """Returns the total number of unique product entries."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        return total or 0


def get_total_stock():
    """Returns the sum of quantities across all products."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM products")
        return cursor.fetchone()[0]


def get_low_stock(threshold=10):
    """Returns the count of products with stock below the given threshold."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < ?", (threshold,))
        return cursor.fetchone()[0] or 0


def get_total_inventory_value():
    """Calculates the total monetary value of current inventory (price * quantity)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(price * quantity), 0.0) FROM products")
        total_value = cursor.fetchone()[0]
        return round(float(total_value), 2)


def get_all_products():
    """Fetches all products ordered by latest added first."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id DESC")
        return cursor.fetchall()


def get_product_by_id(product_id):
    """Retrieves a single product row by its unique ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return cursor.fetchone()


def update_product(product_id, product_name, category, price, quantity, supplier):
    """Updates existing product details by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products
            SET product_name = ?,
                category = ?,
                price = ?,
                quantity = ?,
                supplier = ?
            WHERE id = ?
        """, (
            product_name.strip(),
            category.strip(),
            float(price),
            int(quantity),
            supplier.strip(),
            product_id
        ))
        return cursor.rowcount > 0


def delete_product(product_id):
    """Deletes a product by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return cursor.rowcount > 0


def search_products(keyword):
    """Searches products matching product name, category, or supplier."""
    term = f"%{keyword.strip()}%"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM products
            WHERE product_name LIKE ?
               OR category LIKE ?
               OR supplier LIKE ?
            ORDER BY id DESC
        """, (term, term, term))
        return cursor.fetchall()


def get_categories():
    """Retrieves a sorted list of unique category strings."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category
            FROM products
            WHERE category IS NOT NULL AND TRIM(category) != ''
            ORDER BY category ASC
        """)
        # Extracts raw strings directly so templates don't have to unpack sqlite3.Row dicts
        return [row["category"] for row in cursor.fetchall()]


def filter_products(category):
    """Filters products belonging to a specific category."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM products
            WHERE category = ?
            ORDER BY id DESC
        """, (category.strip(),))
        return cursor.fetchall()

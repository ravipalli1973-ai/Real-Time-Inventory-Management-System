import sqlite3

DATABASE = "data/inventory.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def add_product(product_name, category, price, quantity, supplier):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products
        (product_name, category, price, quantity, supplier)
        VALUES (?, ?, ?, ?, ?)
    """, (product_name, category, price, quantity, supplier))

    conn.commit()
    conn.close()

def get_total_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total = cursor.fetchone()[0]

    conn.close()
    return total


def get_total_stock():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(quantity) FROM products")
    total_stock = cursor.fetchone()[0]

    conn.close()

    if total_stock is None:
        return 0

    return total_stock


def get_low_stock():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 10")
    low_stock = cursor.fetchone()[0]

    conn.close()
    return low_stock
def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    products = cursor.fetchall()

    conn.close()
    return products
def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    conn.close()
    return product


def update_product(product_id, product_name, category, price, quantity, supplier):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET product_name=?,
            category=?,
            price=?,
            quantity=?,
            supplier=?
        WHERE id=?
    """, (
        product_name,
        category,
        price,
        quantity,
        supplier,
        product_id
    ))

    conn.commit()
    conn.close()
def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()
def search_products(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE product_name LIKE ?
        OR category LIKE ?
        OR supplier LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    products = cursor.fetchall()

    conn.close()
    return products
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT category
        FROM products
        ORDER BY category
    """)

    categories = cursor.fetchall()

    conn.close()

    return categories
def filter_products(category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM products
        WHERE category = ?
    """, (category,))

    products = cursor.fetchall()

    conn.close()

    return products
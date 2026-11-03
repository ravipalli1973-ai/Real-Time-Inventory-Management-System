import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE = os.path.join(DATA_DIR, "inventory.db")


def create_database():
    """Initializes the inventory SQLite database and creates the products table."""
    # Ensure the target directory exists before creating the SQLite database
    os.makedirs(DATA_DIR, exist_ok=True)

    # Using context managers ensures automatic commit and proper connection closure
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Enforce foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Create products table with constraints
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL CHECK(length(trim(product_name)) > 0),
            category TEXT NOT NULL CHECK(length(trim(category)) > 0),
            price REAL NOT NULL CHECK(price >= 0.001),
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            supplier TEXT NOT NULL CHECK(length(trim(supplier)) > 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Trigger to automatically update updated_at timestamp on row modifications
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_update_timestamp
        AFTER UPDATE ON products
        FOR EACH ROW
        BEGIN
            UPDATE products
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = OLD.id;
        END;
        """)

        # Indexes for fast search and category filtering in your Flask app
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_category 
        ON products (category);
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_name 
        ON products (product_name);
        """)

        conn.commit()


if __name__ == "__main__":
    create_database()
    print(f"Database created successfully at: {DATABASE}")

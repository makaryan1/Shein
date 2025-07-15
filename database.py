import sqlite3
from pathlib import Path

DATABASE = 'database.db'

def init_db():
    if not Path(DATABASE).exists():
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute('''CREATE TABLE products
                     (id INTEGER PRIMARY KEY,
                      name TEXT,
                      price REAL,
                      image TEXT,
                      category TEXT,
                      description TEXT,
                      rating REAL)''')

        # Тестовые данные
        test_products = [
            (1, "Smartphone X12", 299.99, "https://via.placeholder.com/300", "Electronics", "Latest smartphone", 4.5),
            (2, "Wireless Headphones", 89.99, "https://via.placeholder.com/300", "Electronics", "Noise cancelling", 4.2),
            (3, "Cotton T-Shirt", 19.99, "https://via.placeholder.com/300", "Clothing", "Comfortable", 4.0),
            (4, "Kitchen Blender", 49.99, "https://via.placeholder.com/300", "Home", "Powerful", 4.3),
            (5, "Facial Cream", 29.99, "https://via.placeholder.com/300", "Beauty", "Moisturizing", 4.1),
            (6, "Smart Watch", 159.99, "https://via.placeholder.com/300", "Electronics", "Health tracking", 4.4),
            (7, "Jeans", 39.99, "https://via.placeholder.com/300", "Clothing", "Classic", 4.0),
            (8, "Coffee Maker", 79.99, "https://via.placeholder.com/300", "Home", "Automatic", 4.2),
            (9, "Shampoo", 14.99, "https://via.placeholder.com/300", "Beauty", "Natural", 4.0),
            (10, "Laptop", 899.99, "https://via.placeholder.com/300", "Electronics", "Thin and light", 4.7)
        ]

        for product in test_products:
            c.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?)", product)

        conn.commit()
        conn.close()

def get_products(page=1, per_page=12, category=None, search_query=None, limit=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = "SELECT * FROM products"
    params = []

    if category:
        query += " WHERE category = ?"
        params.append(category)

    if search_query:
        query += (" AND" if category else " WHERE") + " name LIKE ?"
        params.append(f"%{search_query}%")

    if limit:
        query += " LIMIT ?"
        params.append(limit)
    else:
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, (page-1)*per_page])

    c.execute(query, params)
    products = [dict(zip(['id','name','price','image','category','description','rating'], row)) 
               for row in c.fetchall()]
    conn.close()
    return products

def get_categories():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM products")
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories

def get_product_by_id(product_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(['id','name','price','image','category','description','rating'], row))
    return None
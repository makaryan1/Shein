
from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
import json
import os
import sqlite3
import hashlib
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import random
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# Инициализация базы данных пользователей
def init_user_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  is_admin INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Создаем админа если его нет
    admin_exists = c.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1").fetchone()[0]
    if admin_exists == 0:
        admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
                  ('admin', 'admin@site.com', admin_hash, 1))
    
    conn.commit()
    conn.close()

# Инициализация базы данных товаров
def init_products_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  price REAL NOT NULL,
                  image TEXT NOT NULL,
                  category TEXT NOT NULL,
                  description TEXT,
                  rating REAL DEFAULT 4.5,
                  discount INTEGER DEFAULT 0,
                  in_stock INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Добавляем тестовые товары если их нет
    count = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        test_products = [
            ("Смартфон iPhone 15", 999.99, "https://via.placeholder.com/300x300?text=iPhone+15", "Электроника", "Новейший iPhone с отличной камерой", 4.8, 10),
            ("Наушники AirPods Pro", 249.99, "https://via.placeholder.com/300x300?text=AirPods", "Электроника", "Беспроводные наушники с шумоподавлением", 4.7, 15),
            ("Кроссовки Nike", 129.99, "https://via.placeholder.com/300x300?text=Nike+Shoes", "Одежда", "Удобные спортивные кроссовки", 4.6, 25),
            ("Платье летнее", 45.99, "https://via.placeholder.com/300x300?text=Summer+Dress", "Одежда", "Легкое летнее платье", 4.5, 30),
            ("Умные часы", 199.99, "https://via.placeholder.com/300x300?text=Smart+Watch", "Электроника", "Спортивные умные часы", 4.4, 20),
            ("Сумка женская", 79.99, "https://via.placeholder.com/300x300?text=Handbag", "Аксессуары", "Стильная женская сумка", 4.3, 35)
        ]
        
        for product in test_products:
            c.execute("INSERT INTO products (name, price, image, category, description, rating, discount) VALUES (?, ?, ?, ?, ?, ?, ?)", product)
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash):
    return hashlib.sha256(password.encode()).hexdigest() == hash

def create_user(username, email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                  (username, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, is_admin FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return {'id': user[0], 'username': user[1], 'is_admin': user[3]}
    return None

def get_products():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE in_stock = 1 ORDER BY created_at DESC")
    products = []
    for row in c.fetchall():
        products.append({
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'image': row[3],
            'category': row[4],
            'description': row[5],
            'rating': row[6],
            'discount': row[7]
        })
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ? AND in_stock = 1", (product_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'image': row[3],
            'category': row[4],
            'description': row[5],
            'rating': row[6],
            'discount': row[7]
        }
    return None

# Загружаем переводы
def load_translations(lang='en'):
    try:
        with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('translations/en.json', 'r', encoding='utf-8') as f:
            return json.load(f)

# Языки
LANGUAGES = {
    'en': {'name': 'English', 'icon': '🇺🇸'},
    'ru': {'name': 'Русский', 'icon': '🇷🇺'},
    'ka': {'name': 'ქართული', 'icon': '🇬🇪'}
}

# Функция для получения товаров с Shein (имитация)
def scrape_shein_products(query="clothes", limit=10):
    """Имитация скрапинга товаров с Shein"""
    fake_products = []
    categories = ["Одежда", "Обувь", "Аксессуары", "Красота", "Дом"]
    
    for i in range(limit):
        product = {
            "name": f"Shein {query.capitalize()} {i+1}",
            "price": round(random.uniform(15.99, 199.99), 2),
            "image": f"https://picsum.photos/300/300?random={random.randint(1000, 9999)}",
            "category": random.choice(categories),
            "description": f"Стильный {query} от Shein",
            "rating": round(random.uniform(4.0, 5.0), 1),
            "discount": random.randint(20, 70)
        }
        fake_products.append(product)
    
    return fake_products

@app.route('/')
def index():
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    products = get_products()
    
    return render_template('index.html', 
                         products=products,
                         cart_count=len(session.get('cart', [])),
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/set_language/<language>')
def set_language(language):
    if language in LANGUAGES:
        session['language'] = language
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    cart_ids = session.get('cart', [])
    cart_items = []
    total = 0
    
    for product_id in cart_ids:
        product = get_product_by_id(int(product_id))
        if product:
            discounted_price = product['price'] * (1 - product['discount'] / 100)
            product['discounted_price'] = discounted_price
            cart_items.append(product)
            total += discounted_price
    
    return render_template('cart.html', 
                         cart=cart_items,
                         total=total,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    if str(product_id) not in session['cart']:
        session['cart'].append(str(product_id))
        flash('Товар добавлен в корзину!', 'success')
    else:
        flash('Товар уже в корзине!', 'info')
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        session['cart'].remove(str(product_id))
        flash('Товар удален из корзины!', 'info')
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    flash('Корзина очищена!', 'info')
    return redirect(url_for('cart'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Пароли не совпадают!', 'error')
        elif create_user(username, email, password):
            flash('Регистрация успешна! Теперь войдите в систему.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пользователь с таким email уже существует!', 'error')
    
    return render_template('register.html', 
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = verify_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash(f'Добро пожаловать, {user["username"]}!', 'success')
            
            if user['is_admin']:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль!', 'error')
    
    return render_template('login.html',
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы!', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Войдите в систему для доступа к профилю!', 'error')
        return redirect(url_for('login'))
    
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    
    return render_template('profile.html',
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# АДМИН ПАНЕЛЬ
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = []
    for row in c.fetchall():
        products.append({
            'id': row[0], 'name': row[1], 'price': row[2], 'image': row[3],
            'category': row[4], 'description': row[5], 'rating': row[6],
            'discount': row[7], 'in_stock': row[8]
        })
    conn.close()
    
    return render_template('admin_panel.html', products=products)

@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    data = request.json
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("""INSERT INTO products (name, price, image, category, description, rating, discount) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (data['name'], data['price'], data['image'], data['category'], 
               data['description'], data.get('rating', 4.5), data.get('discount', 0)))
    conn.commit()
    conn.close()
    
    flash('Товар добавлен!', 'success')
    return jsonify({'success': True})

@app.route('/admin/edit_product/<int:product_id>', methods=['POST'])
def admin_edit_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    data = request.json
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("""UPDATE products SET name=?, price=?, image=?, category=?, 
                 description=?, rating=?, discount=? WHERE id=?""",
              (data['name'], data['price'], data['image'], data['category'],
               data['description'], data['rating'], data['discount'], product_id))
    conn.commit()
    conn.close()
    
    flash('Товар обновлен!', 'success')
    return jsonify({'success': True})

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("UPDATE products SET in_stock = 0 WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    flash('Товар удален!', 'success')
    return jsonify({'success': True})

@app.route('/admin/discount_all', methods=['POST'])
def admin_discount_all():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    discount = request.json.get('discount', 20)
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("UPDATE products SET price = price * ? WHERE in_stock = 1", ((100 - discount) / 100,))
    conn.commit()
    conn.close()
    
    flash(f'Цены снижены на {discount}%!', 'success')
    return jsonify({'success': True})

@app.route('/admin/import_shein', methods=['POST'])
def admin_import_shein():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    query = request.json.get('query', 'clothes')
    limit = request.json.get('limit', 10)
    
    try:
        products = scrape_shein_products(query, limit)
        
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        
        added_count = 0
        for product in products:
            c.execute("""INSERT INTO products (name, price, image, category, description, rating, discount) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (product['name'], product['price'], product['image'], product['category'],
                       product['description'], product['rating'], product['discount']))
            added_count += 1
        
        conn.commit()
        conn.close()
        
        flash(f'Добавлено {added_count} товаров из Shein!', 'success')
        return jsonify({'success': True, 'added': added_count})
    
    except Exception as e:
        flash(f'Ошибка импорта: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search():
    query = request.args.get('q', '')
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    
    if query:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE name LIKE ? AND in_stock = 1", (f'%{query}%',))
        products = []
        for row in c.fetchall():
            products.append({
                'id': row[0], 'name': row[1], 'price': row[2], 'image': row[3],
                'category': row[4], 'description': row[5], 'rating': row[6], 'discount': row[7]
            })
        conn.close()
    else:
        products = []
    
    return render_template('search_results.html',
                         products=products,
                         query=query,
                         cart_count=len(session.get('cart', [])),
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

if __name__ == '__main__':
    # Создаем папки если их нет
    Path("templates").mkdir(exist_ok=True)
    Path("static/css").mkdir(exist_ok=True, parents=True)
    Path("static/js").mkdir(exist_ok=True, parents=True)
    Path("translations").mkdir(exist_ok=True)
    
    # Инициализируем базы данных
    init_user_db()
    init_products_db()

    # Создаем файлы переводов если их нет
    translations_files = {
        'en.json': {
            "Online Shopping": "Online Shopping",
            "Categories": "Categories",
            "Add to Cart": "Add to Cart",
            "Cart": "Cart",
            "Profile": "Profile",
            "Login": "Login",
            "Register": "Register",
            "Search": "Search"
        },
        'ru.json': {
            "Online Shopping": "Онлайн-магазин",
            "Categories": "Категории",
            "Add to Cart": "В корзину",
            "Cart": "Корзина",
            "Profile": "Профиль",
            "Login": "Войти",
            "Register": "Регистрация",
            "Search": "Поиск"
        }
    }
    
    for filename, content in translations_files.items():
        if not os.path.exists(f'translations/{filename}'):
            with open(f'translations/{filename}', 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)

    app.run(host='0.0.0.0', port=5000, debug=True)

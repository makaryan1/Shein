
from flask import Flask, render_template, session, redirect, url_for, request
import json
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-123'

# Система переводов
TRANSLATIONS = {
    'en': {
        'Online Shopping': 'Online Store',
        'Categories': 'Categories',
        'All Categories': 'All Categories',
        'Add to Cart': 'Add to Cart',
        'Search': 'Search',
        'Cart': 'Cart',
        'Home': 'Home',
        'welcome': 'Welcome to our store!',
        'change_language': 'Change language'
    },
    'ru': {
        'Online Shopping': 'Интернет-магазин',
        'Categories': 'Категории',
        'All Categories': 'Все категории',
        'Add to Cart': 'В корзину',
        'Search': 'Поиск',
        'Cart': 'Корзина',
        'Home': 'Главная',
        'welcome': 'Добро пожаловать в наш магазин!',
        'change_language': 'Сменить язык'
    },
    'ka': {
        'Online Shopping': 'ონლაინ მაღაზია',
        'Categories': 'კატეგორიები',
        'All Categories': 'ყველა კატეგორია',
        'Add to Cart': 'კალათაში დამატება',
        'Search': 'ძებნა',
        'Cart': 'კალათა',
        'Home': 'მთავარი',
        'welcome': 'კეთილი იყოს თქვენი მობრძანება!',
        'change_language': 'ენის შეცვლა'
    }
}

LANGUAGES = {
    'en': 'English',
    'ru': 'Русский',
    'ka': 'ქართული'
}

# Загружаем товары из JSON
def load_products():
    if os.path.exists('products.json'):
        with open('products.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    lang = session.get('language', 'en')
    products = load_products()
    return render_template('index.html',
                         _=TRANSLATIONS[lang],
                         products=products,
                         languages=LANGUAGES,
                         current_lang=lang)

@app.route('/set_language/<language>')
def set_language(language):
    if language in LANGUAGES:
        session['language'] = language
    return redirect(url_for('index'))

# Корзина
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    products = load_products()
    cart_items = [p for p in products if str(p['id']) in cart]
    return render_template('cart.html', cart=cart_items)

# Добавление в корзину
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(str(product_id))
    return redirect(url_for('index'))

# Очистка корзины
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

if __name__ == '__main__':
    # Создаем папку templates если ее нет
    Path("templates").mkdir(exist_ok=True)
    
    # Создаем товары если их нет
    if not os.path.exists('products.json'):
        sample_products = [
            {"id": 1, "name": "Футболка", "price": "25.99 $", "image": "https://picsum.photos/300/200?random=1"},
            {"id": 2, "name": "Джинсы", "price": "79.99 $", "image": "https://picsum.photos/300/200?random=2"},
            {"id": 3, "name": "Кроссовки", "price": "120.00 $", "image": "https://picsum.photos/300/200?random=3"}
        ]
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(sample_products, f, ensure_ascii=False, indent=2)
    
    app.run(host='0.0.0.0', port=3000, debug=True)

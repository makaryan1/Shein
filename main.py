
from flask import Flask, render_template, session, request
import json
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# Загружаем переводы
def load_translations(lang='en'):
    try:
        with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Если файл перевода не найден, возвращаем английский
        with open('translations/en.json', 'r', encoding='utf-8') as f:
            return json.load(f)

# Языки
LANGUAGES = {
    'en': {'name': 'English', 'icon': '🇺🇸'},
    'ru': {'name': 'Русский', 'icon': '🇷🇺'},
    'ka': {'name': 'ქართული', 'icon': '🇬🇪'}
}

# Данные товаров
PRODUCTS = [
    {"id": 1, "name": "Смартфон X12", "price": 299.99, "image": "https://via.placeholder.com/200x200?text=Phone", "category": "Электроника"},
    {"id": 2, "name": "Наушники", "price": 89.99, "image": "https://via.placeholder.com/200x200?text=Headphones", "category": "Электроника"},
    {"id": 3, "name": "Футболка", "price": 19.99, "image": "https://via.placeholder.com/200x200?text=T-Shirt", "category": "Одежда"}
]

@app.route('/')
def index():
    # Получаем текущий язык из сессии или используем английский по умолчанию
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    
    return render_template('index.html', 
                         products=PRODUCTS,
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
    cart = session.get('cart', [])
    cart_items = [p for p in PRODUCTS if str(p['id']) in cart]
    return render_template('cart.html', 
                         cart=cart_items,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(str(product_id))
    return redirect(url_for('index'))

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

if __name__ == '__main__':
    from flask import redirect, url_for
    
    # Создаем папки если их нет
    Path("templates").mkdir(exist_ok=True)
    Path("static/images").mkdir(exist_ok=True, parents=True)
    Path("translations").mkdir(exist_ok=True)

    # Создаем файлы переводов если их нет
    if not os.path.exists('translations/en.json'):
        with open('translations/en.json', 'w', encoding='utf-8') as f:
            json.dump({
                "Online Shopping": "Online Shopping",
                "Categories": "Categories",
                "Add to Cart": "Add to Cart"
            }, f, ensure_ascii=False, indent=2)

    if not os.path.exists('translations/ru.json'):
        with open('translations/ru.json', 'w', encoding='utf-8') as f:
            json.dump({
                "Online Shopping": "Онлайн-магазин",
                "Categories": "Категории", 
                "Add to Cart": "В корзину"
            }, f, ensure_ascii=False, indent=2)

    app.run(host='0.0.0.0', port=5000, debug=True)

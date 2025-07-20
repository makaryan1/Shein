from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from authlib.integrations.flask_client import OAuth
import hashlib
import random
import time
from datetime import datetime, timedelta
import requests
import uuid
import re
from bs4 import BeautifulSoup

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-fallback-secret-key')

# Конфигурация Supabase
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("ОШИБКА: Переменные окружения SUPABASE_URL и SUPABASE_KEY не найдены!")
    print("Пожалуйста, добавьте их в Secrets вашего Repl:")
    print("1. Откройте инструмент Secrets")
    print("2. Добавьте SUPABASE_URL = https://your-project-ref.supabase.co")
    print("3. Добавьте SUPABASE_KEY = your-anon-key")
    exit(1)

print(f"Подключение к Supabase: {supabase_url}")
supabase: Client = create_client(supabase_url, supabase_key)

# SHEIN API функции
class SheinScraper:
    def __init__(self):
        self.base_url = "https://www.shein.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_categories(self):
        """Получить список категорий"""
        return [
            {'id': 'women-clothing', 'name': 'Женская одежда', 'url': '/women-clothing-c-1727.html'},
            {'id': 'men-clothing', 'name': 'Мужская одежда', 'url': '/men-clothing-c-1728.html'},
            {'id': 'shoes', 'name': 'Обувь', 'url': '/shoes-c-1729.html'},
            {'id': 'bags', 'name': 'Сумки', 'url': '/bags-c-1730.html'},
            {'id': 'accessories', 'name': 'Аксессуары', 'url': '/accessories-c-1731.html'},
            {'id': 'beauty', 'name': 'Красота', 'url': '/beauty-c-1732.html'},
            {'id': 'home', 'name': 'Дом', 'url': '/home-c-1733.html'},
            {'id': 'sports', 'name': 'Спорт', 'url': '/sports-c-1734.html'}
        ]

    def scrape_products(self, category_id, limit=50, markup=30):
        """Скрапинг товаров из категории"""
        try:
            # Генерируем фейковые товары для демонстрации
            products = []
            categories = self.get_categories()
            category_name = next((cat['name'] for cat in categories if cat['id'] == category_id), 'Одежда')

            # Разнообразные изображения для разных категорий
            image_sets = {
                'women-clothing': [
                    'https://img.ltwebstatic.com/images3_pi/2024/01/02/170528187642513446_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/03/170528188942513447_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/04/170528189642513448_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/05/170528190642513449_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/06/170528191642513450_thumbnail_405x552.jpg'
                ],
                'men-clothing': [
                    'https://img.ltwebstatic.com/images3_pi/2024/01/07/170528192642513451_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/08/170528193642513452_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/09/170528194642513453_thumbnail_405x552.jpg'
                ],
                'shoes': [
                    'https://img.ltwebstatic.com/images3_pi/2024/01/10/170528195642513454_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/11/170528196642513455_thumbnail_405x552.jpg'
                ],
                'bags': [
                    'https://img.ltwebstatic.com/images3_pi/2024/01/12/170528197642513456_thumbnail_405x552.jpg',
                    'https://img.ltwebstatic.com/images3_pi/2024/01/13/170528198642513457_thumbnail_405x552.jpg'
                ]
            }

            # Используем изображения по умолчанию если категория не найдена
            default_images = [
                'https://via.placeholder.com/405x552/FF6F43/FFFFFF?text=SHEIN+Product',
                'https://via.placeholder.com/405x552/FF69B4/FFFFFF?text=Fashion+Item',
                'https://via.placeholder.com/405x552/4169E1/FFFFFF?text=Trendy+Style',
                'https://via.placeholder.com/405x552/32CD32/FFFFFF?text=New+Arrival',
                'https://via.placeholder.com/405x552/FF4500/FFFFFF?text=Hot+Deal'
            ]

            for i in range(limit):
                # Выбираем изображения для категории
                category_images = image_sets.get(category_id, default_images)
                main_image = random.choice(category_images)

                # Генерируем дополнительные изображения для галереи
                additional_images = random.sample(category_images, min(3, len(category_images)))

                product = {
                    'shein_id': f'shein_{category_id}_{i+1}',
                    'name': self.generate_product_name(category_name, i+1),
                    'original_price': round(random.uniform(10, 200), 2),
                    'price': 0,  # Будет рассчитана с наценкой
                    'image': main_image,
                    'images': additional_images,  # Галерея изображений
                    'category': category_name,
                    'description': self.generate_description(category_name),
                    'rating': round(random.uniform(4.0, 5.0), 1),
                    'discount': random.randint(10, 60),
                    'colors': self.generate_colors(),
                    'sizes': self.generate_sizes(category_id),
                    'reviews_count': random.randint(50, 5000),
                    'in_stock': True,
                    'specifications': self.generate_specifications(category_id),
                    'shipping_info': self.generate_shipping_info()
                }

                # Применяем наценку
                product['price'] = round(product['original_price'] * (1 + markup / 100), 2)
                products.append(product)

            return products

        except Exception as e:
            print(f"Ошибка при скрапинге товаров: {e}")
            return []

    def generate_specifications(self, category_id):
        """Генерация характеристик товара"""
        base_specs = {
            'Бренд': 'SHEIN',
            'Происхождение': 'Китай',
            'Качество': 'Премиум'
        }

        if category_id in ['women-clothing', 'men-clothing']:
            base_specs.update({
                'Материал': random.choice(['Хлопок', 'Полиэстер', 'Вискоза', 'Смесь тканей']),
                'Уход': 'Машинная стирка при 30°C',
                'Сезон': random.choice(['Весна-Лето', 'Осень-Зима', 'Всесезонный'])
            })
        elif category_id == 'shoes':
            base_specs.update({
                'Материал верха': random.choice(['Кожа', 'Текстиль', 'Синтетика']),
                'Материал подошвы': 'Резина',
                'Высота каблука': f'{random.randint(0, 10)} см'
            })
        elif category_id == 'bags':
            base_specs.update({
                'Материал': random.choice(['Кожа PU', 'Текстиль', 'Нейлон']),
                'Размеры': f'{random.randint(20, 40)}x{random.randint(15, 30)}x{random.randint(5, 15)} см',
                'Застежка': random.choice(['Молния', 'Магнит', 'Кнопка'])
            })

        return base_specs

    def generate_shipping_info(self):
        """Генерация информации о доставке"""
        return {
            'standard_delivery': '5-7 рабочих дней',
            'express_delivery': '1-3 рабочих дня',
            'free_shipping_threshold': 50,
            'return_policy': '30 дней бесплатного возврата'
        }

    def generate_product_name(self, category, index):
        """Генерация названий товаров"""
        templates = {
            'Женская одежда': [
                'Элегантное платье с цветочным принтом',
                'Стильная блуза с рукавами-фонариками',
                'Модная юбка-миди',
                'Трендовый топ-кроп',
                'Уютный свитер оверсайз'
            ],
            'Мужская одежда': [
                'Классическая рубашка',
                'Спортивные брюки',
                'Модная футболка',
                'Стильная куртка',
                'Удобные джинсы'
            ],
            'Обувь': [
                'Стильные кроссовки',
                'Элегантные туфли',
                'Удобные босоножки',
                'Модные ботинки',
                'Спортивные кеды'
            ],
            'Сумки': [
                'Элегантная сумка',
                'Стильный рюкзак',
                'Модный клатч',
                'Практичная сумка-тоут',
                'Трендовая поясная сумка'
            ]
        }

        names = templates.get(category, ['Модный товар'])
        return f"{random.choice(names)} #{index}"

    def generate_description(self, category):
        """Генерация описаний товаров"""
        descriptions = [
            'Высококачественный товар из премиальных материалов',
            'Стильный и современный дизайн для любого случая',
            'Удобная посадка и отличное качество',
            'Модный тренд этого сезона',
            'Идеальное сочетание стиля и комфорта'
        ]
        return random.choice(descriptions)

    def generate_colors(self):
        """Генерация доступных цветов"""
        colors = ['Черный', 'Белый', 'Красный', 'Синий', 'Зеленый', 'Розовый', 'Желтый', 'Серый']
        return random.sample(colors, random.randint(2, 5))

    def generate_sizes(self, category_id):
        """Генерация размеров"""
        if category_id in ['women-clothing', 'men-clothing']:
            return ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        elif category_id == 'shoes':
            return ['36', '37', '38', '39', '40', '41', '42', '43', '44']
        else:
            return ['One Size']

# Инициализация скрапера
shein_scraper = SheinScraper()

# Функции для работы с пользователями
def create_user_in_supabase(email, username, password=None, provider=None, provider_id=None):
    try:
        # Проверяем, существует ли пользователь
        existing_user = get_user_by_email(email)
        if existing_user:
            return None

        # Создаем админа если это первый пользователь
        is_admin = email == 'admin@temuclone.com'

        user_data = {
            'email': email,
            'username': username,
            'password_hash': hashlib.sha256(password.encode()).hexdigest() if password else None,
            'provider': provider or 'email',
            'provider_id': provider_id,
            'is_admin': is_admin
        }

        result = supabase.table('users').insert(user_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def create_admin_user():
    """Создает админа при первом запуске"""
    try:
        admin_email = 'admin@temuclone.com'
        admin_password = 'AdminTemu2024!@#'

        # Проверяем, существует ли админ
        existing_admin = get_user_by_email(admin_email)
        if not existing_admin:
            admin_data = {
                'email': admin_email,
                'username': 'Administrator',
                'password_hash': hashlib.sha256(admin_password.encode()).hexdigest(),
                'provider': 'email',
                'provider_id': None,
                'is_admin': True
            }

            result = supabase.table('users').insert(admin_data).execute()
            if result.data:
                print(f"Admin user created: {admin_email} / {admin_password}")
                # Создаем тестовые товары
                create_sample_products()
    except Exception as e:
        print(f"Error creating admin: {e}")

def get_user_by_email(email):
    try:
        result = supabase.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def verify_password(password, hash_password):
    return hashlib.sha256(password.encode()).hexdigest() == hash_password

def create_sample_products():
    """Создает тестовые товары"""
    try:
        # Проверяем, есть ли уже товары
        existing_products = supabase.table('products').select('id').limit(1).execute()
        if existing_products.data:
            return

        # Создаем товары из каждой категории
        categories = shein_scraper.get_categories()
        for category in categories[:3]:  # Берем первые 3 категории
            products = shein_scraper.scrape_products(category['id'], limit=10)

            for product in products:
                product_data = {
                    'name': product['name'],
                    'price': product['price'],
                    'image': product['image'],
                    'category': product['category'],
                    'description': product['description'],
                    'rating': product['rating'],
                    'discount': product['discount'],
                    'in_stock': product['in_stock']
                }

                supabase.table('products').insert(product_data).execute()

        print("Sample products created successfully")
    except Exception as e:
        print(f"Error creating sample products: {e}")

# Функции для работы с товарами
def get_products(limit=None, category=None, search=None):
    try:
        query = supabase.table('products').select('*').eq('in_stock', True)

        if category:
            query = query.eq('category', category)

        if search:
            query = query.ilike('name', f'%{search}%')

        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

def get_product_by_id(product_id):
    try:
        result = supabase.table('products').select('*').eq('id', product_id).eq('in_stock', True).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting product: {e}")
        return None

def get_categories():
    try:
        result = supabase.table('products').select('category').execute()
        categories = list(set([item['category'] for item in result.data]))
        return categories
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

# Функции для работы с корзиной
def get_cart_items(user_id):
    try:
        result = supabase.table('cart').select('*, products(*)').eq('user_id', user_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting cart items: {e}")
        return []

def add_to_cart_db(user_id, product_id, quantity=1):
    try:
        # Проверяем, есть ли уже товар в корзине
        existing = supabase.table('cart').select('*').eq('user_id', user_id).eq('product_id', product_id).execute()

        if existing.data:
            # Обновляем количество
            supabase.table('cart').update({'quantity': existing.data[0]['quantity'] + quantity}).eq('id', existing.data[0]['id']).execute()
        else:
            # Добавляем новый товар
            supabase.table('cart').insert({
                'user_id': user_id,
                'product_id': product_id,
                'quantity': quantity,
                'created_at': datetime.now().isoformat()
            }).execute()

        return True
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return False

def remove_from_cart_db(user_id, product_id):
    try:
        supabase.table('cart').delete().eq('user_id', user_id).eq('product_id', product_id).execute()
        return True
    except Exception as e:
        print(f"Error removing from cart: {e}")
        return False

def update_cart_quantity(user_id, product_id, quantity):
    try:
        if quantity <= 0:
            return remove_from_cart_db(user_id, product_id)

        supabase.table('cart').update({'quantity': quantity}).eq('user_id', user_id).eq('product_id', product_id).execute()
        return True
    except Exception as e:
        print(f"Error updating cart quantity: {e}")
        return False

# Языки и переводы
LANGUAGES = {
    'en': {'name': 'English', 'icon': '🇺🇸'},
    'ru': {'name': 'Русский', 'icon': '🇷🇺'},
    'ka': {'name': 'ქართული', 'icon': '🇬🇪'},
    'fr': {'name': 'Français', 'icon': '🇫🇷'},
    'de': {'name': 'Deutsch', 'icon': '🇩🇪'},
    'es': {'name': 'Español', 'icon': '🇪🇸'},
    'it': {'name': 'Italiano', 'icon': '🇮🇹'},
    'pt': {'name': 'Português', 'icon': '🇵🇹'},
    'ar': {'name': 'العربية', 'icon': '🇸🇦'},
    'zh': {'name': '中文', 'icon': '🇨🇳'}
}

def load_translations(lang='en'):
    try:
        with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('translations/en.json', 'r', encoding='utf-8') as f:
            return json.load(f)

# Главная страница
@app.route('/')
def index():
    # Создаем админа при первом запуске
    create_admin_user()

    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)

    # Получаем товары
    products = get_products(limit=24)
    categories = get_categories()

    # Получаем популярные товары
    popular_products = get_products(limit=8)

    return render_template('index.html', 
                         products=products,
                         categories=categories,
                         popular_products=popular_products,
                         cart_count=len(get_cart_items(session['user_id'])) if 'user_id' in session else len(session.get('cart', [])),
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# Страница товара
@app.route('/product/<string:product_id>')
def product_detail(product_id):
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)

    product = get_product_by_id(product_id)
    if not product:
        flash('Товар не найден', 'error')
        return redirect(url_for('index'))

    # Похожие товары
    similar_products = get_products(limit=4, category=product['category'])
    similar_products = [p for p in similar_products if p['id'] != product_id]

    return render_template('product_detail.html',
                         product=product,
                         similar_products=similar_products,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# Поиск
@app.route('/search')
def search():
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)

    query = request.args.get('q', '')
    category = request.args.get('category', '')

    products = get_products(search=query, category=category if category else None)

    return render_template('search_results.html',
                         products=products,
                         query=query,
                         category=category,
                         categories=get_categories(),
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# Корзина
@app.route('/cart')
def cart():
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)

    if 'user_id' in session:
        # Для зарегистрированных пользователей
        cart_items = get_cart_items(session['user_id'])
        total = sum(item['quantity'] * item['products']['price'] * (1 - item['products']['discount'] / 100) for item in cart_items)
    else:
        # Для гостей
        cart_ids = session.get('cart', [])
        cart_items = []
        total = 0

        for product_id in cart_ids:
            product = get_product_by_id(product_id)
            if product:
                discounted_price = product['price'] * (1 - product['discount'] / 100)
                cart_items.append({
                    'products': product,
                    'quantity': 1,
                    'total_price': discounted_price
                })
                total += discounted_price

    return render_template('cart.html',
                         cart_items=cart_items,
                         total=total,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# Добавление в корзину
@app.route('/add_to_cart/<string:product_id>')
def add_to_cart(product_id):
    if 'user_id' in session:
        # Для зарегистрированных пользователей
        if add_to_cart_db(session['user_id'], product_id):
            flash('Товар добавлен в корзину!', 'success')
        else:
            flash('Ошибка при добавлении товара', 'error')
    else:
        # Для гостей
        if 'cart' not in session:
            session['cart'] = []

        if str(product_id) not in session['cart']:
            session['cart'].append(str(product_id))
            flash('Товар добавлен в корзину!', 'success')
        else:
            flash('Товар уже в корзине!', 'info')

    return redirect(url_for('index'))

# API для обновления корзины
@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Необходимо войти в систему'}), 401

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if update_cart_quantity(session['user_id'], product_id, quantity):
        cart_items = get_cart_items(session['user_id'])
        cart_count = sum(item['quantity'] for item in cart_items)
        return jsonify({'success': True, 'cart_count': cart_count})

    return jsonify({'error': 'Ошибка обновления корзины'}), 500

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Необходимо войти в систему'}), 401

    data = request.get_json()
    product_id = data.get('product_id')

    if remove_from_cart_db(session['user_id'], product_id):
        cart_items = get_cart_items(session['user_id'])
        cart_count = sum(item['quantity'] for item in cart_items)
        return jsonify({'success': True, 'cart_count': cart_count})

    return jsonify({'error': 'Ошибка удаления из корзины'}), 500

# Языки
@app.route('/set_language/<language>')
def set_language(language):
    if language in LANGUAGES:
        session['language'] = language
    return redirect(url_for('index'))

# Регистрация
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
        else:
            user = create_user_in_supabase(email, username, password)
            if user:
                flash('Регистрация успешна! Теперь войдите в систему.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка регистрации. Возможно, пользователь уже существует.', 'error')

    return render_template('register.html',
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['is_admin'] = user['is_admin']

            # Переносим корзину гостя в базу данных
            if 'cart' in session:
                for product_id in session['cart']:
                    add_to_cart_db(user['id'], product_id)
                session.pop('cart', None)

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

# Выход
@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы!', 'info')
    return redirect(url_for('index'))

# Профиль
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

# Админ панель
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('index'))

    products = get_products()
    categories = get_categories()
    shein_categories = shein_scraper.get_categories()

    # Статистика
    try:
        total_products = len(products)
        total_users = len(supabase.table('users').select('id').execute().data)
        total_orders = len(supabase.table('orders').select('id').execute().data) if supabase.table('orders').select('id').execute().data else 0

        stats = {
            'total_products': total_products,
            'total_users': total_users,
            'total_orders': total_orders
        }
    except:
        stats = {
            'total_products': 0,
            'total_users': 0,
            'total_orders': 0
        }

    return render_template('admin_panel.html',
                         products=products,
                         categories=categories,
                         shein_categories=shein_categories,
                         stats=stats)

# Импорт товаров из SHEIN
@app.route('/admin/import_shein', methods=['POST'])
def admin_import_shein():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        data = request.json
        category_id = data.get('category_id')
        limit = data.get('limit', 50)
        markup = data.get('markup', 30)

        if not category_id:
            return jsonify({'error': 'Категория не выбрана'}), 400

        # Получаем товары из SHEIN
        products = shein_scraper.scrape_products(category_id, limit, markup)

        if not products:
            return jsonify({'error': 'Не удалось получить товары'}), 500

        # Сохраняем товары в базу данных
        saved_count = 0
        for product in products:
            try:
                # Подготавливаем дополнительные данные
                additional_data = {
                    'images': json.dumps(product.get('images', [])),
                    'colors': json.dumps(product.get('colors', [])),
                    'sizes': json.dumps(product.get('sizes', [])),
                    'specifications': json.dumps(product.get('specifications', {})),
                    'shipping_info': json.dumps(product.get('shipping_info', {})),
                    ```python
                    'tags': json.dumps(product.get('tags', [])),
                    'brand': product.get('brand', 'SHEIN'),
                    'material': product.get('material', ''),
                    'care_instructions': product.get('care_instructions', ''),
                    'reviews_count': product.get('reviews_count', 0)
                }

                product_data = {
                    'name': product['name'],
                    'price': product['price'],
                    'image': product['image'],
                    'category': product['category'],
                    'description': product['description'],
                    'rating': product['rating'],
                    'discount': product['discount'],
                    'in_stock': True,
                    'created_at': datetime.now().isoformat(),
                    **additional_data
                }

                result = supabase.table('products').insert(product_data).execute()
                if result.data:
                    saved_count += 1
            except Exception as e:
                print(f"Ошибка при сохранении товара: {e}")
                continue

        return jsonify({
            'success': True, 
            'imported': saved_count,
            'total': len(products)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Добавление товара (админ)
@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        data = request.json
        result = supabase.table('products').insert({
            'name': data['name'],
            'price': data['price'],
            'image': data['image'],
            'category': data['category'],
            'description': data['description'],
            'rating': data.get('rating', 4.5),
            'discount': data.get('discount', 0),
            'in_stock': True,
            'created_at': datetime.now().isoformat()
        }).execute()

        if result.data:
            return jsonify({'success': True, 'product': result.data[0]})
        else:
            return jsonify({'error': 'Ошибка при добавлении товара'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Редактирование товара (админ)
@app.route('/admin/edit_product/<string:product_id>', methods=['POST'])
def admin_edit_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        data = request.json
        result = supabase.table('products').update({
            'name': data['name'],
            'price': data['price'],
            'image': data['image'],
            'category': data['category'],
            'description': data['description'],
            'rating': data['rating'],
            'discount': data['discount']
        }).eq('id', product_id).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Удаление товара (админ)
@app.route('/admin/delete_product/<string:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        supabase.table('products').update({'in_stock': False}).eq('id', product_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Применение скидки (админ)
@app.route('/admin/apply_discount', methods=['POST'])
def admin_apply_discount():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        data = request.json
        product_ids = data.get('product_ids', [])
        discount = data.get('discount', 0)

        if not product_ids:
            return jsonify({'error': 'Товары не выбраны'}), 400

        # Применяем скидку к выбранным товарам
        for product_id in product_ids:
            supabase.table('products').update({'discount': discount}).eq('id', product_id).execute()

        return jsonify({'success': True, 'updated': len(product_ids)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Оформление заказа
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Войдите в систему для оформления заказа!', 'error')
        return redirect(url_for('login'))

    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)

    if request.method == 'POST':
        try:
            # Получаем данные формы
            order_data = {
                'first_name': request.form['firstName'],
                'last_name': request.form['lastName'],
                'email': request.form['email'],
                'phone': request.form['phone'],
                'country': request.form['country'],
                'city': request.form['city'],
                'address': request.form['address'],
                'apartment': request.form.get('apartment', ''),
                'postal_code': request.form.get('postalCode', ''),
                'additional_info': request.form.get('additionalInfo', ''),
                'payment_method': request.form['paymentMethod']
            }

            # Получаем товары из корзины
            cart_items = get_cart_items(session['user_id'])
            if not cart_items:
                flash('Ваша корзина пуста!', 'error')
                return redirect(url_for('cart'))

            # Рассчитываем общую сумму
            total_amount = sum(item['quantity'] * item['products']['price'] * (1 - item['products']['discount'] / 100) for item in cart_items)

            # Создаем заказ
            order_id = str(uuid.uuid4())
            order_result = supabase.table('orders').insert({
                'id': order_id,
                'user_id': session['user_id'],
                'status': 'pending',
                'total_amount': total_amount,
                'shipping_address': f"{order_data['address']}, {order_data['apartment']}, {order_data['city']}, {order_data['country']}",
                'customer_info': json.dumps(order_data),
                'created_at': datetime.now().isoformat()
            }).execute()

            # Добавляем товары в заказ
            for item in cart_items:
                supabase.table('order_items').insert({
                    'order_id': order_id,
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': item['products']['price'] * (1 - item['products']['discount'] / 100)
                }).execute()

            # Очищаем корзину
            supabase.table('cart').delete().eq('user_id', session['user_id']).execute()

            # Отправляем уведомление админу
            send_order_notification(order_id, order_data, cart_items, total_amount)

            flash('Заказ успешно оформлен! Вы получите уведомление о статусе доставки.', 'success')
            return redirect(url_for('order_success', order_id=order_id))

        except Exception as e:
            print(f"Error creating order: {e}")
            flash('Ошибка при оформлении заказа. Попробуйте снова.', 'error')

    # GET запрос - показываем форму оформления заказа
    cart_items = get_cart_items(session['user_id'])
    if not cart_items:
        flash('Ваша корзина пуста!', 'error')
        return redirect(url_for('cart'))

    total = sum(item['quantity'] * item['products']['price'] * (1 - item['products']['discount'] / 100) for item in cart_items)

    return render_template('checkout.html',
                         cart_items=cart_items,
                         total=total,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# Страница успешного заказа
@app.route('/order_success/<order_id>')
def order_success(order_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))

    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)

    # Получаем информацию о заказе
    try:
        order_result = supabase.table('orders').select('*').eq('id', order_id).eq('user_id', session['user_id']).execute()
        if not order_result.data:
            flash('Заказ не найден!', 'error')
            return redirect(url_for('index'))

        order = order_result.data[0]

        # Получаем товары заказа
        order_items_result = supabase.table('order_items').select('*, products(*)').eq('order_id', order_id).execute()
        order_items = order_items_result.data

        return render_template('order_success.html',
                             order=order,
                             order_items=order_items,
                             _=translations,
                             current_lang=current_lang,
                             languages=LANGUAGES)

    except Exception as e:
        print(f"Error getting order: {e}")
        flash('Ошибка при получении информации о заказе', 'error')
        return redirect(url_for('index'))

def send_order_notification(order_id, order_data, cart_items, total_amount):
    """Отправляет уведомление админу о новом заказе"""
    try:
        # Формируем сообщение для админа
        message = f"""
🛒 НОВЫЙ ЗАКАЗ #{order_id[:8]}

👤 ИНФОРМАЦИЯ О ПОКУПАТЕЛЕ:
Имя: {order_data['first_name']} {order_data['last_name']}
Email: {order_data['email']}
Телефон: {order_data['phone']}

📍 АДРЕС ДОСТАВКИ:
Страна: {order_data['country']}
Город: {order_data['city']}
Адрес: {order_data['address']}
Квартира: {order_data.get('apartment', 'Не указана')}
Индекс: {order_data.get('postal_code', 'Не указан')}
Дополнительная информация: {order_data.get('additional_info', 'Нет')}

🛍️ ТОВАРЫ:
"""

        for item in cart_items:
            price = item['products']['price'] * (1 - item['products']['discount'] / 100)
            message += f"• {item['products']['name']} x{item['quantity']} - ${price:.2f}\n"
            if item['products']['discount'] > 0:
                message += f"  (скидка {item['products']['discount']}%)\n"

        message += f"""
💰 ОБЩАЯ СУММА: ${total_amount:.2f}
💳 СПОСОБ ОПЛАТЫ: {order_data['payment_method']}

🕐 Время заказа: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Для обработки заказа свяжитесь с покупателем и организуйте доставку.
        """

        # В реальном приложении здесь можно отправить:
        # - Email админу
        # - SMS уведомление
        # - Push уведомление
        # - Webhook в систему управления заказами

        print("=== УВЕДОМЛЕНИЕ О НОВОМ ЗАКАЗЕ ===")
        print(message)
        print("=== КОНЕЦ УВЕДОМЛЕНИЯ ===")

        # Сохраняем уведомление в базу данных
        supabase.table('notifications').insert({
            'type': 'new_order',
            'title': f'Новый заказ #{order_id[:8]}',
            'message': message,
            'order_id': order_id,
            'is_read': False,
            'created_at': datetime.now().isoformat()
        }).execute()

    except Exception as e:
        print(f"Error sending order notification: {e}")

if __name__ == '__main__':
    # Use debug=False for production deployment
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
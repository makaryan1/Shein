import os
import json
import uuid
import hashlib
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup

# Конфигурация логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    """Централизованная конфигурация приложения"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-fallback-secret-key')
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    DEBUG = os.getenv('FLASK_ENV') == 'development'

    # Бизнес-константы
    DEFAULT_MARKUP = 30
    CART_SESSION_KEY = 'cart'
    LANGUAGE_SESSION_KEY = 'language'
    DEFAULT_LANGUAGE = 'en'

class SheinProductGenerator:
    """Профессиональный генератор продуктов с реалистичными данными"""

    def __init__(self):
        self.categories_data = {
            'women-clothing': {
                'name': 'Женская одежда',
                'products': [
                    'Элегантное платье с цветочным принтом',
                    'Стильная блуза с рукавами-фонариками', 
                    'Модная юбка-миди',
                    'Трендовый топ-кроп',
                    'Уютный свитер оверсайз',
                    'Летнее платье-макси',
                    'Кардиган из мягкого трикотажа',
                    'Деловой костюм',
                    'Джинсы скинни',
                    'Романтичная блузка'
                ],
                'colors': ['Черный', 'Белый', 'Бежевый', 'Розовый', 'Синий', 'Красный'],
                'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'materials': ['Хлопок', 'Полиэстер', 'Вискоза', 'Смесь тканей', 'Шелк']
            },
            'men-clothing': {
                'name': 'Мужская одежда',
                'products': [
                    'Классическая рубашка',
                    'Спортивные брюки',
                    'Модная футболка',
                    'Стильная куртка',
                    'Удобные джинсы',
                    'Поло с воротником',
                    'Худи оверсайз',
                    'Деловые брюки',
                    'Кожаная куртка',
                    'Спортивный костюм'
                ],
                'colors': ['Черный', 'Белый', 'Серый', 'Синий', 'Зеленый', 'Коричневый'],
                'sizes': ['S', 'M', 'L', 'XL', 'XXL', 'XXXL'],
                'materials': ['Хлопок', 'Деним', 'Полиэстер', 'Кожа', 'Флис']
            },
            'shoes': {
                'name': 'Обувь',
                'products': [
                    'Стильные кроссовки',
                    'Элегантные туфли',
                    'Удобные босоножки',
                    'Модные ботинки',
                    'Спортивные кеды',
                    'Зимние сапоги',
                    'Летние шлепанцы',
                    'Деловые оксфорды',
                    'Высокие сапоги',
                    'Мокасины'
                ],
                'colors': ['Черный', 'Коричневый', 'Белый', 'Серый', 'Красный'],
                'sizes': ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45'],
                'materials': ['Кожа', 'Текстиль', 'Замша', 'Синтетика', 'Резина']
            },
            'bags': {
                'name': 'Сумки',
                'products': [
                    'Элегантная сумка',
                    'Стильный рюкзак',
                    'Модный клатч',
                    'Практичная сумка-тоут',
                    'Трендовая поясная сумка',
                    'Кожаная сумка через плечо',
                    'Спортивная сумка',
                    'Вечерний клатч',
                    'Деловой портфель',
                    'Туристический рюкзак'
                ],
                'colors': ['Черный', 'Коричневый', 'Бежевый', 'Красный', 'Синий'],
                'sizes': ['One Size'],
                'materials': ['Кожа PU', 'Натуральная кожа', 'Текстиль', 'Нейлон']
            }
        }

    def generate_products(self, category_id: str, limit: int = 50, markup: int = 30) -> List[Dict]:
        """Генерирует реалистичные продукты для категории"""
        if category_id not in self.categories_data:
            return []

        category = self.categories_data[category_id]
        products = []

        for i in range(limit):
            product = self._create_product(category_id, category, i + 1, markup)
            products.append(product)

        return products

    def _create_product(self, category_id: str, category: Dict, index: int, markup: int) -> Dict:
        """Создает один продукт с реалистичными характеристиками"""
        base_price = random.uniform(15, 250)
        discount = random.randint(5, 70)
        final_price = round(base_price * (1 + markup / 100), 2)

        return {
            'shein_id': f'shein_{category_id}_{index}',
            'name': f"{random.choice(category['products'])} #{index}",
            'original_price': round(base_price, 2),
            'price': final_price,
            'image': self._generate_product_image(category_id, index),
            'images': self._generate_image_gallery(category_id),
            'category': category['name'],
            'description': self._generate_description(),
            'rating': round(random.uniform(4.0, 5.0), 1),
            'discount': discount,
            'colors': random.sample(category['colors'], random.randint(2, 4)),
            'sizes': category['sizes'],
            'reviews_count': random.randint(50, 5000),
            'in_stock': True,
            'specifications': self._generate_specifications(category_id, category),
            'shipping_info': self._generate_shipping_info(),
            'tags': self._generate_tags(category_id),
            'brand': 'SHEIN',
            'material': random.choice(category['materials']),
            'care_instructions': 'Машинная стирка при 30°C',
            'country_origin': 'Китай'
        }

    def _generate_product_image(self, category_id: str, index: int) -> str:
        """Генерирует URL изображения продукта"""
        # Используем разные источники изображений для лучшего качества
        image_sources = [
            f'https://picsum.photos/405/552?random={category_id}{index}',
            f'https://source.unsplash.com/405x552/?fashion,{category_id}',
            f'https://loremflickr.com/405/552/fashion,clothing?random={index}',
            f'https://via.placeholder.com/405x552/7B68EE/FFFFFF?text=SHEIN+Product+{index}'
        ]
        return random.choice(image_sources)

    def _generate_image_gallery(self, category_id: str) -> List[str]:
        """Генерирует галерею изображений"""
        gallery = []
        for i in range(1, 5):
            # Разные стили изображений для галереи
            sources = [
                f'https://picsum.photos/405/552?random={category_id}{i}{random.randint(1000, 9999)}',
                f'https://source.unsplash.com/405x552/?{category_id},fashion,style',
                f'https://loremflickr.com/405/552/{category_id},style?random={i}{random.randint(100, 999)}'
            ]
            gallery.append(random.choice(sources))
        return gallery

    def _generate_description(self) -> str:
        """Генерирует описание продукта"""
        descriptions = [
            'Премиальное качество материалов и современный дизайн',
            'Идеальное сочетание комфорта и стиля для повседневной носки',
            'Трендовая модель из новой коллекции с уникальным кроем',
            'Универсальный вариант для создания стильных образов',
            'Высококачественный товар с отличными отзывами покупателей'
        ]
        return random.choice(descriptions)

    def _generate_specifications(self, category_id: str, category: Dict) -> Dict:
        """Генерирует технические характеристики"""
        specs = {
            'Бренд': 'SHEIN',
            'Материал': random.choice(category['materials']),
            'Происхождение': 'Китай',
            'Уход': 'Следуйте инструкциям на ярлыке'
        }

        if category_id in ['women-clothing', 'men-clothing']:
            specs['Сезон'] = random.choice(['Весна-Лето', 'Осень-Зима', 'Всесезонный'])
        elif category_id == 'shoes':
            specs['Высота каблука'] = f'{random.randint(0, 10)} см'

        return specs

    def _generate_shipping_info(self) -> Dict:
        """Генерирует информацию о доставке"""
        return {
            'standard_delivery': '5-7 рабочих дней',
            'express_delivery': '1-3 рабочих дня',
            'free_shipping_threshold': 50,
            'return_policy': '30 дней бесплатного возврата'
        }

    def _generate_tags(self, category_id: str) -> List[str]:
        """Генерирует теги для продукта"""
        all_tags = {
            'women-clothing': ['fashion', 'trendy', 'elegant', 'casual', 'formal'],
            'men-clothing': ['classic', 'sporty', 'business', 'casual', 'modern'],
            'shoes': ['comfortable', 'stylish', 'durable', 'athletic', 'formal'],
            'bags': ['practical', 'stylish', 'spacious', 'elegant', 'casual']
        }
        return random.sample(all_tags.get(category_id, ['trendy']), random.randint(2, 4))

class DatabaseManager:
    """Профессиональный менеджер базы данных"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    def create_user(self, email: str, username: str, password: str = None, 
                   provider: str = 'email', provider_id: str = None) -> Optional[Dict]:
        """Создает нового пользователя"""
        try:
            if self.get_user_by_email(email):
                return None

            user_data = {
                'email': email,
                'username': username,
                'password_hash': hashlib.sha256(password.encode()).hexdigest() if password else None,
                'provider': provider,
                'provider_id': provider_id,
                'is_admin': email == 'admin@sheinmarket.com',
                'created_at': datetime.now().isoformat()
            }

            result = self.supabase.table('users').insert(user_data).execute()
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Получает пользователя по email"""
        try:
            result = self.supabase.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def verify_password(self, password: str, hash_password: str) -> bool:
        """Проверяет пароль"""
        return hashlib.sha256(password.encode()).hexdigest() == hash_password

    def get_products(self, limit: int = None, category: str = None, 
                    search: str = None, page: int = 1, per_page: int = 24) -> List[Dict]:
        """Получает продукты с поддержкой пагинации и фильтрации"""
        try:
            query = self.supabase.table('products').select('*').eq('in_stock', True)

            if category:
                query = query.eq('category', category)

            if search:
                query = query.ilike('name', f'%{search}%')

            if limit:
                query = query.limit(limit)
            else:
                offset = (page - 1) * per_page
                query = query.range(offset, offset + per_page - 1)

            result = query.execute()
            return result.data

        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []

    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Получает продукт по ID"""
        try:
            result = self.supabase.table('products').select('*').eq('id', product_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return None

    def add_product(self, product_data: Dict) -> Optional[Dict]:
        """Добавляет новый продукт"""
        try:
            product_data['created_at'] = datetime.now().isoformat()
            result = self.supabase.table('products').insert(product_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            return None

class CartManager:
    """Профессиональный менеджер корзины"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> bool:
        """Добавляет товар в корзину"""
        try:
            existing = self.db.supabase.table('cart').select('*')\
                .eq('user_id', user_id).eq('product_id', product_id).execute()

            if existing.data:
                new_quantity = existing.data[0]['quantity'] + quantity
                self.db.supabase.table('cart').update({'quantity': new_quantity})\
                    .eq('id', existing.data[0]['id']).execute()
            else:
                self.db.supabase.table('cart').insert({
                    'user_id': user_id,
                    'product_id': product_id,
                    'quantity': quantity,
                    'created_at': datetime.now().isoformat()
                }).execute()

            return True
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            return False

    def get_cart_items(self, user_id: str) -> List[Dict]:
        """Получает товары из корзины"""
        try:
            result = self.db.supabase.table('cart').select('*, products(*)')\
                .eq('user_id', user_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting cart items: {e}")
            return []

    def update_quantity(self, user_id: str, product_id: str, quantity: int) -> bool:
        """Обновляет количество товара в корзине"""
        try:
            if quantity <= 0:
                return self.remove_from_cart(user_id, product_id)

            self.db.supabase.table('cart').update({'quantity': quantity})\
                .eq('user_id', user_id).eq('product_id', product_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating cart quantity: {e}")
            return False

    def remove_from_cart(self, user_id: str, product_id: str) -> bool:
        """Удаляет товар из корзины"""
        try:
            self.db.supabase.table('cart').delete()\
                .eq('user_id', user_id).eq('product_id', product_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error removing from cart: {e}")
            return False

# Инициализация приложения
app = Flask(__name__)
app.config.from_object(Config)

# Проверка конфигурации
if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
    logger.error("Missing Supabase configuration!")
    exit(1)

# Инициализация сервисов
supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
db_manager = DatabaseManager(supabase_client)
cart_manager = CartManager(db_manager)
product_generator = SheinProductGenerator()

# Языки
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

def load_translations(lang: str = 'en') -> Dict:
    """Загружает переводы"""
    try:
        with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('translations/en.json', 'r', encoding='utf-8') as f:
            return json.load(f)

def create_admin_user():
    """Создает администратора при первом запуске"""
    admin_email = 'admin@sheinmarket.com'
    admin_password = 'AdminShein2024!@#'

    if not db_manager.get_user_by_email(admin_email):
        admin = db_manager.create_user(admin_email, 'Administrator', admin_password)
        if admin:
            logger.info(f"Admin created: {admin_email} / {admin_password}")

def create_sample_products():
    """Создает образцы продуктов"""
    try:
        existing = db_manager.get_products(limit=1)
        if existing:
            return

        categories = ['women-clothing', 'men-clothing', 'shoes', 'bags']
        for category_id in categories:
            products = product_generator.generate_products(category_id, limit=15)

            for product in products:
                product_data = {
                    'name': product['name'],
                    'price': product['price'],
                    'image': product['image'],
                    'category': product['category'],
                    'description': product['description'],
                    'rating': product['rating'],
                    'discount': product['discount'],
                    'in_stock': True
                }
                db_manager.add_product(product_data)

        logger.info("Sample products created")
    except Exception as e:
        logger.error(f"Error creating sample products: {e}")

# Routes
@app.route('/')
def index():
    create_admin_user()
    create_sample_products()

    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    products = db_manager.get_products(limit=24)
    popular_products = db_manager.get_products(limit=8)

    categories = list(set([p['category'] for p in db_manager.get_products(limit=100)]))

    cart_count = 0
    if 'user_id' in session:
        cart_items = cart_manager.get_cart_items(session['user_id'])
        cart_count = sum(item['quantity'] for item in cart_items)
    else:
        cart_count = len(session.get(Config.CART_SESSION_KEY, []))

    return render_template('index.html',
                         products=products,
                         categories=categories,
                         popular_products=popular_products,
                         cart_count=cart_count,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/product/<string:product_id>')
def product_detail(product_id):
    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    product = db_manager.get_product_by_id(product_id)
    if not product:
        flash('Товар не найден', 'error')
        return redirect(url_for('index'))

    similar_products = db_manager.get_products(limit=4, category=product['category'])
    similar_products = [p for p in similar_products if p['id'] != product_id]

    return render_template('product_detail.html',
                         product=product,
                         similar_products=similar_products,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/search')
def search():
    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    query = request.args.get('q', '')
    category = request.args.get('category', '')
    page = int(request.args.get('page', 1))

    products = db_manager.get_products(
        search=query if query else None,
        category=category if category else None,
        page=page
    )

    categories = list(set([p['category'] for p in db_manager.get_products(limit=100)]))

    return render_template('search_results.html',
                         products=products,
                         query=query,
                         category=category,
                         categories=categories,
                         current_page=page,
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/cart')
def cart():
    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    cart_items = []
    total = 0

    if 'user_id' in session:
        cart_items = cart_manager.get_cart_items(session['user_id'])
        total = sum(
            item['quantity'] * item['products']['price'] * (1 - item['products']['discount'] / 100)
            for item in cart_items
        )
    else:
        cart_ids = session.get(Config.CART_SESSION_KEY, [])
        for product_id in cart_ids:
            product = db_manager.get_product_by_id(product_id)
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

@app.route('/add_to_cart/<string:product_id>')
def add_to_cart(product_id):
    if 'user_id' in session:
        if cart_manager.add_to_cart(session['user_id'], product_id):
            flash('Товар добавлен в корзину!', 'success')
        else:
            flash('Ошибка при добавлении товара', 'error')
    else:
        cart = session.get(Config.CART_SESSION_KEY, [])
        if str(product_id) not in cart:
            cart.append(str(product_id))
            session[Config.CART_SESSION_KEY] = cart
            flash('Товар добавлен в корзину!', 'success')
        else:
            flash('Товар уже в корзине!', 'info')

    return redirect(url_for('index'))

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Необходимо войти в систему'}), 401

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if cart_manager.update_quantity(session['user_id'], product_id, quantity):
        cart_items = cart_manager.get_cart_items(session['user_id'])
        cart_count = sum(item['quantity'] for item in cart_items)
        return jsonify({'success': True, 'cart_count': cart_count})

    return jsonify({'error': 'Ошибка обновления корзины'}), 500

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Необходимо войти в систему'}), 401

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if cart_manager.add_to_cart(session['user_id'], product_id, quantity):
        cart_items = cart_manager.get_cart_items(session['user_id'])
        cart_count = sum(item['quantity'] for item in cart_items)
        return jsonify({'success': True, 'cart_count': cart_count})

    return jsonify({'error': 'Ошибка добавления в корзину'}), 500

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Необходимо войти в систему'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    
    if cart_manager.remove_from_cart(session['user_id'], product_id):
        cart_items = cart_manager.get_cart_items(session['user_id'])
        cart_count = sum(item['quantity'] for item in cart_items)
        return jsonify({'success': True, 'cart_count': cart_count})
    
    return jsonify({'error': 'Ошибка удаления из корзины'}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Пароли не совпадают!', 'error')
        else:
            user = db_manager.create_user(email, username, password)
            if user:
                flash('Регистрация успешна!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка регистрации. Пользователь уже существует.', 'error')

    return render_template('register.html',
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db_manager.get_user_by_email(email)
        if user and db_manager.verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['is_admin'] = user['is_admin']

            # Переносим корзину гостя
            if Config.CART_SESSION_KEY in session:
                for product_id in session[Config.CART_SESSION_KEY]:
                    cart_manager.add_to_cart(user['id'], product_id)
                session.pop(Config.CART_SESSION_KEY, None)

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

@app.route('/set_language/<language>')
def set_language(language):
    if language in LANGUAGES:
        session[Config.LANGUAGE_SESSION_KEY] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы!', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Войдите в систему!', 'error')
        return redirect(url_for('login'))

    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    return render_template('profile.html',
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        flash('Доступ запрещен!', 'error')
        return redirect(url_for('index'))

    products = db_manager.get_products(limit=100)
    categories = list(set([p['category'] for p in products]))

    # Статистика
    try:
        stats = {
            'total_products': len(products),
            'total_users': len(supabase_client.table('users').select('id').execute().data),
            'total_orders': len(supabase_client.table('orders').select('id').execute().data or [])
        }
    except:
        stats = {'total_products': 0, 'total_users': 0, 'total_orders': 0}

    return render_template('admin_panel.html',
                         products=products,
                         categories=categories,
                         stats=stats)

@app.route('/admin/import_shein', methods=['POST'])
def admin_import_shein():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        data = request.json
        category_id = data.get('category_id')
        limit = data.get('limit', 50)
        markup = data.get('markup', 30)

        products = product_generator.generate_products(category_id, limit, markup)

        saved_count = 0
        for product in products:
            product_data = {
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'category': product['category'],
                'description': product['description'],
                'rating': product['rating'],
                'discount': product['discount'],
                'in_stock': True
            }

            if db_manager.add_product(product_data):
                saved_count += 1

        return jsonify({
            'success': True,
            'imported': saved_count,
            'total': len(products)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        data = request.json
        product_data = {
            'name': data['name'],
            'price': data['price'],
            'image': data['image'],
            'category': data['category'],
            'description': data['description'],
            'rating': data.get('rating', 4.5),
            'discount': data.get('discount', 0),
            'in_stock': True,
        }
        product = db_manager.add_product(product_data)

        if product:
            return jsonify({'success': True, 'product': product})
        else:
            return jsonify({'error': 'Ошибка при добавлении товара'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/edit_product/<string:product_id>', methods=['POST'])
def admin_edit_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        data = request.json
        product_data = {
            'name': data['name'],
            'price': data['price'],
            'image': data['image'],
            'category': data['category'],
            'description': data['description'],
            'rating': data['rating'],
            'discount': data['discount']
        }
        result = supabase_client.table('products').update(product_data).eq('id', product_id).execute()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete_product/<string:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403

    try:
        supabase_client.table('products').update({'in_stock': False}).eq('id', product_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            supabase_client.table('products').update({'discount': discount}).eq('id', product_id).execute()

        return jsonify({'success': True, 'updated': len(product_ids)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Оформление заказа
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Войдите в систему для оформления заказа!', 'error')
        return redirect(url_for('login'))

    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
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
            cart_items = cart_manager.get_cart_items(session['user_id'])
            if not cart_items:
                flash('Ваша корзина пуста!', 'error')
                return redirect(url_for('cart'))

            # Рассчитываем общую сумму
            total_amount = sum(item['quantity'] * item['products']['price'] * (1 - item['products']['discount'] / 100) for item in cart_items)

            # Создаем заказ
            order_id = str(uuid.uuid4())
            order_result = supabase_client.table('orders').insert({
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
                supabase_client.table('order_items').insert({
                    'order_id': order_id,
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': item['products']['price'] * (1 - item['products']['discount'] / 100)
                }).execute()

            # Очищаем корзину
            cart_manager.db.supabase.table('cart').delete().eq('user_id', session['user_id']).execute()

            # Отправляем уведомление админу
            send_order_notification(order_id, order_data, cart_items, total_amount)

            flash('Заказ успешно оформлен! Вы получите уведомление о статусе доставки.', 'success')
            return redirect(url_for('order_success', order_id=order_id))

        except Exception as e:
            print(f"Error creating order: {e}")
            flash('Ошибка при оформлении заказа. Попробуйте снова.', 'error')

    # GET запрос - показываем форму оформления заказа
    cart_items = cart_manager.get_cart_items(session['user_id'])
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

    current_lang = session.get(Config.LANGUAGE_SESSION_KEY, Config.DEFAULT_LANGUAGE)
    translations = load_translations(current_lang)

    # Получаем информацию о заказе
    try:
        order_result = supabase_client.table('orders').select('*').eq('id', order_id).eq('user_id', session['user_id']).execute()
        if not order_result.data:
            flash('Заказ не найден!', 'error')
            return redirect(url_for('index'))

        order = order_result.data[0]
        
        # Получаем товары заказа
        order_items_result = supabase_client.table('order_items').select('*, products(*)').eq('order_id', order_id).execute()
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
        supabase_client.table('notifications').insert({
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
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
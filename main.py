
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

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-fallback-secret-key')

# Инициализация Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Инициализация OAuth
oauth = OAuth(app)

# Настройка Google OAuth
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Настройка Facebook OAuth
facebook = oauth.register(
    name='facebook',
    client_id=os.getenv('FACEBOOK_APP_ID'),
    client_secret=os.getenv('FACEBOOK_APP_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email'},
)

# Функции для работы с пользователями
def create_user_in_supabase(email, username, password=None, provider=None, provider_id=None):
    try:
        user_data = {
            'email': email,
            'username': username,
            'password_hash': hashlib.sha256(password.encode()).hexdigest() if password else None,
            'provider': provider or 'email',
            'provider_id': provider_id,
            'is_admin': False,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user_by_email(email):
    try:
        result = supabase.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def verify_password(password, hash_password):
    return hashlib.sha256(password.encode()).hexdigest() == hash_password

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

# Языки и переводы
LANGUAGES = {
    'en': {'name': 'English', 'icon': '🇺🇸'},
    'ru': {'name': 'Русский', 'icon': '🇷🇺'},
    'ka': {'name': 'ქართული', 'icon': '🇬🇪'}
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
    current_lang = session.get('language', 'en')
    translations = load_translations(current_lang)
    
    # Получаем товары
    products = get_products(limit=20)
    categories = get_categories()
    
    # Получаем популярные товары
    popular_products = get_products(limit=8)
    
    return render_template('index.html', 
                         products=products,
                         categories=categories,
                         popular_products=popular_products,
                         cart_count=len(session.get('cart', [])),
                         _=translations,
                         current_lang=current_lang,
                         languages=LANGUAGES)

# Страница товара
@app.route('/product/<int:product_id>')
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
            product = get_product_by_id(int(product_id))
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
@app.route('/add_to_cart/<int:product_id>')
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
                    add_to_cart_db(user['id'], int(product_id))
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

# Google OAuth
@app.route('/auth/google')
def google_auth():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        email = user_info['email']
        name = user_info['name']
        
        # Проверяем, есть ли пользователь
        user = get_user_by_email(email)
        
        if not user:
            # Создаем нового пользователя
            user = create_user_in_supabase(email, name, provider='google', provider_id=user_info['sub'])
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['is_admin'] = user['is_admin']
            
            flash(f'Добро пожаловать, {user["username"]}!', 'success')
            return redirect(url_for('index'))
    
    flash('Ошибка авторизации через Google', 'error')
    return redirect(url_for('login'))

# Facebook OAuth
@app.route('/auth/facebook')
def facebook_auth():
    redirect_uri = url_for('facebook_callback', _external=True)
    return facebook.authorize_redirect(redirect_uri)

@app.route('/auth/facebook/callback')
def facebook_callback():
    token = facebook.authorize_access_token()
    
    if token:
        resp = facebook.get('me?fields=id,name,email')
        user_info = resp.json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        
        if email:
            # Проверяем, есть ли пользователь
            user = get_user_by_email(email)
            
            if not user:
                # Создаем нового пользователя
                user = create_user_in_supabase(email, name, provider='facebook', provider_id=user_info['id'])
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                session['is_admin'] = user['is_admin']
                
                flash(f'Добро пожаловать, {user["username"]}!', 'success')
                return redirect(url_for('index'))
    
    flash('Ошибка авторизации через Facebook', 'error')
    return redirect(url_for('login'))

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
                         stats=stats)

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
@app.route('/admin/edit_product/<int:product_id>', methods=['POST'])
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
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    try:
        supabase.table('products').update({'in_stock': False}).eq('id', product_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Импорт товаров
@app.route('/admin/import_products', methods=['POST'])
def admin_import_products():
    if not session.get('is_admin'):
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    try:
        # Генерируем фейковые товары для демонстрации
        fake_products = []
        categories = ["Электроника", "Одежда", "Дом", "Красота", "Спорт"]
        
        for i in range(10):
            product = {
                'name': f'Товар {i+1}',
                'price': round(random.uniform(10, 500), 2),
                'image': f'https://picsum.photos/400/400?random={random.randint(1, 1000)}',
                'category': random.choice(categories),
                'description': f'Описание товара {i+1}',
                'rating': round(random.uniform(3.5, 5.0), 1),
                'discount': random.randint(0, 50),
                'in_stock': True,
                'created_at': datetime.now().isoformat()
            }
            fake_products.append(product)
        
        # Вставляем в базу данных
        result = supabase.table('products').insert(fake_products).execute()
        
        return jsonify({'success': True, 'added': len(result.data)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

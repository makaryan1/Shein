from flask import Flask, render_template, request, session, redirect, url_for
import json

app = Flask(__name__)
app.secret_key = "your_secret_key_123"

# Загружаем товары из JSON
def load_products():
    with open('products.json', 'r') as f:
        return json.load(f)

# Главная страница
@app.route('/')
def index():
    products = load_products()
    return render_template('index.html', products=products)

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
    app.run(host='0.0.0.0', port=5000)
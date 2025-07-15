from flask import Flask, render_template, session
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# Данные товаров
PRODUCTS = [
    {"id": 1, "name": "Смартфон X12", "price": 299.99, "image": "phone.jpg", "category": "Электроника"},
    {"id": 2, "name": "Наушники", "price": 89.99, "image": "headphones.jpg", "category": "Электроника"},
    {"id": 3, "name": "Футболка", "price": 19.99, "image": "tshirt.jpg", "category": "Одежда"}
]

@app.route('/')
def index():
    return render_template('index.html', 
                         products=PRODUCTS,
                         cart_count=len(session.get('cart', [])))

if __name__ == '__main__':
    # Создаем папки если их нет
    Path("templates").mkdir(exist_ok=True)
    Path("static/images").mkdir(exist_ok=True, parents=True)

    # Создаем базовый шаблон
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Мой магазин</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .product-card {
            transition: transform 0.3s;
            margin-bottom: 20px;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .product-image {
            height: 200px;
            object-fit: contain;
            padding: 10px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Мой магазин</a>
            <a href="/cart" class="btn btn-light">
                Корзина <span class="badge bg-danger">{{ cart_count }}</span>
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            {% for product in products %}
            <div class="col-md-4">
                <div class="card product-card">
                    <img src="/static/images/{{ product.image }}" class="card-img-top product-image" alt="{{ product.name }}">
                    <div class="card-body">
                        <h5 class="card-title">{{ product.name }}</h5>
                        <p class="card-text text-danger">{{ product.price }} ₽</p>
                        <button class="btn btn-primary">В корзину</button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')

    app.run(host='0.0.0.0', port=5000, debug=True)
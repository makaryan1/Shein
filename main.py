from flask import Flask, render_template, session, redirect, url_for
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-123'

# Простая система переводов
TRANSLATIONS = {
    'en': {
        'title': 'Online Store',
        'welcome': 'Welcome to our store!',
        'change_language': 'Change language'
    },
    'ru': {
        'title': 'Интернет-магазин',
        'welcome': 'Добро пожаловать в наш магазин!',
        'change_language': 'Сменить язык'
    },
    'ka': {
        'title': 'ონლაინ მაღაზია',
        'welcome': 'კეთილი იყოს თქვენი მობრძანება!',
        'change_language': 'ენის შეცვლა'
    }
}

LANGUAGES = {
    'en': 'English',
    'ru': 'Русский',
    'ka': 'ქართული'
}

@app.route('/')
def index():
    lang = session.get('language', 'en')
    return render_template('index.html',
                         t=TRANSLATIONS[lang],
                         languages=LANGUAGES,
                         current_lang=lang)

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in LANGUAGES:
        session['language'] = lang
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Создаем папку templates если ее нет
    Path("templates").mkdir(exist_ok=True)

    # Создаем базовый шаблон если его нет
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html lang="{{ current_lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ t.title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .language-selector {
            margin: 20px 0;
        }
        .language-selector a {
            margin-right: 10px;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <h1>{{ t.welcome }}</h1>

    <div class="language-selector">
        <h3>{{ t.change_language }}:</h3>
        {% for code, name in languages.items() %}
            <a href="{{ url_for('set_language', lang=code) }}">
                {{ name }}
            </a>
        {% endfor %}
    </div>

    <p>Current language code: {{ current_lang }}</p>
</body>
</html>''')

    app.run(host='0.0.0.0', port=5000, debug=True)
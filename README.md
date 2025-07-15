
# TemuClone - Интернет-магазин

Полнофункциональный интернет-магазин в стиле Temu с интеграцией Supabase и OAuth авторизацией.

## 🚀 Функциональность

- 🛍️ Каталог товаров с поиском и фильтрацией
- 🛒 Корзина покупок
- 👤 Регистрация и авторизация (email, Google, Facebook)
- 📱 Адаптивный дизайн
- 🔐 Админ панель с управлением товарами
- 🌐 Многоязычность (EN, RU, KA)
- 💳 Интеграция с Supabase

## 🛠️ Установка и настройка

### 1. Настройка Supabase

1. Создайте проект в [Supabase](https://supabase.com)
2. Выполните SQL скрипт из файла `supabase_schema.sql` в SQL Editor
3. Получите URL и anon key из Settings > API

### 2. Настройка OAuth

#### Google OAuth:
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API
4. Создайте OAuth 2.0 credentials
5. Добавьте redirect URI: `https://your-domain.com/auth/google/callback`

#### Facebook OAuth:
1. Перейдите в [Facebook Developers](https://developers.facebook.com)
2. Создайте новое приложение
3. Добавьте Facebook Login продукт
4. Настройте Valid OAuth Redirect URIs: `https://your-domain.com/auth/facebook/callback`

### 3. Настройка переменных окружения

Создайте файл `.env` и заполните его:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FLASK_SECRET_KEY=your-secret-key
```

### 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 5. Запуск приложения

```bash
python main.py
```

## 👤 Админ аккаунт

- Email: admin@site.com
- Пароль: admin123

## 📁 Структура проекта

```
├── main.py              # Основное приложение
├── templates/           # HTML шаблоны
├── static/             # CSS, JS, изображения
├── translations/       # Файлы переводов
├── requirements.txt    # Зависимости Python
├── supabase_schema.sql # SQL схема для Supabase
└── README.md          # Документация
```

## 🔧 Основные возможности

### Для пользователей:
- Просмотр каталога товаров
- Поиск и фильтрация
- Добавление в корзину
- Регистрация/авторизация
- Смена языка интерфейса

### Для администраторов:
- Управление товарами (CRUD)
- Импорт товаров
- Применение скидок
- Просмотр статистики
- Управление пользователями

## 🌐 Технологии

- **Backend**: Python, Flask
- **Database**: Supabase (PostgreSQL)
- **Authentication**: OAuth 2.0 (Google, Facebook)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Icons**: Font Awesome

## 📱 Адаптивность

Приложение полностью адаптировано под мобильные устройства и планшеты.

## 🔐 Безопасность

- Хеширование паролей
- OAuth 2.0 авторизация
- Защита от SQL инъекций
- Валидация данных

## 📈 Будущие обновления

- Система оплаты
- Отзывы и рейтинги
- Уведомления
- Чат поддержки
- Аналитика продаж

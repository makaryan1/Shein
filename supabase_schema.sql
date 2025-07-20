
-- Создание таблицы пользователей
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255),
    provider VARCHAR(50) DEFAULT 'email',
    provider_id VARCHAR(255),
    is_admin BOOLEAN DEFAULT false,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы товаров
CREATE TABLE products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    rating DECIMAL(3,2) DEFAULT 4.5,
    discount INTEGER DEFAULT 0,
    in_stock BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы корзины
CREATE TABLE cart (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Создание таблицы заказов
CREATE TABLE orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address TEXT,
    customer_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы элементов заказа
CREATE TABLE order_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы избранного
CREATE TABLE favorites (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Создание таблицы уведомлений
CREATE TABLE notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    order_id UUID,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для оптимизации
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_in_stock ON products(in_stock);
CREATE INDEX idx_cart_user_id ON cart(user_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- Вставка тестовых данных
INSERT INTO users (email, username, password_hash, is_admin) VALUES
('admin@site.com', 'admin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', true);

INSERT INTO products (name, price, image, category, description, rating, discount) VALUES
('Смартфон iPhone 15', 999.99, 'https://via.placeholder.com/400x400?text=iPhone+15', 'Электроника', 'Новейший iPhone с отличной камерой', 4.8, 10),
('Наушники AirPods Pro', 249.99, 'https://via.placeholder.com/400x400?text=AirPods', 'Электроника', 'Беспроводные наушники с шумоподавлением', 4.7, 15),
('Кроссовки Nike Air Max', 129.99, 'https://via.placeholder.com/400x400?text=Nike+Shoes', 'Одежда', 'Удобные спортивные кроссовки', 4.6, 25),
('Платье летнее', 45.99, 'https://via.placeholder.com/400x400?text=Summer+Dress', 'Одежда', 'Легкое летнее платье', 4.5, 30),
('Умные часы Apple Watch', 399.99, 'https://via.placeholder.com/400x400?text=Apple+Watch', 'Электроника', 'Спортивные умные часы', 4.4, 20),
('Сумка женская', 79.99, 'https://via.placeholder.com/400x400?text=Handbag', 'Аксессуары', 'Стильная женская сумка', 4.3, 35),
('Ноутбук MacBook Pro', 1999.99, 'https://via.placeholder.com/400x400?text=MacBook', 'Электроника', 'Профессиональный ноутбук', 4.9, 5),
('Джинсы классические', 69.99, 'https://via.placeholder.com/400x400?text=Jeans', 'Одежда', 'Классические джинсы', 4.2, 40);

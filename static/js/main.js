
/**
 * SHEIN Market - Профессиональный JavaScript
 * Современное решение с ES6+, TypeScript-подобными типами и лучшими практиками
 */

class SheinMarket {
    constructor() {
        this.cart = new CartManager();
        this.ui = new UIManager();
        this.notifications = new NotificationManager();
        this.search = new SearchManager();
        this.wishlist = new WishlistManager();
        this.filters = new FilterManager();
        
        this.init();
    }

    /**
     * Инициализация приложения
     */
    init() {
        this.bindEvents();
        this.ui.init();
        this.cart.init();
        this.initIntersectionObserver();
        this.initServiceWorker();
    }

    /**
     * Привязка событий
     */
    bindEvents() {
        // Поиск
        const searchForm = document.querySelector('.search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => this.search.handleSearch(e));
        }

        // Быстрый поиск
        const searchInput = document.querySelector('#search-input');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.search.quickSearch(e.target.value);
                }, 300);
            });
        }

        // Кнопки добавления в корзину
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-cart-btn')) {
                e.preventDefault();
                const productId = e.target.dataset.productId;
                this.cart.addItem(productId);
            }

            // Wishlist
            if (e.target.matches('.wishlist-btn')) {
                e.preventDefault();
                const productId = e.target.dataset.productId;
                this.wishlist.toggleItem(productId);
            }

            // Quick view
            if (e.target.matches('.quick-view-btn')) {
                e.preventDefault();
                const productId = e.target.dataset.productId;
                this.ui.showQuickView(productId);
            }
        });

        // Фильтры
        document.addEventListener('change', (e) => {
            if (e.target.matches('.filter-input')) {
                this.filters.applyFilters();
            }
        });

        // Прокрутка для загрузки больше товаров
        window.addEventListener('scroll', this.ui.throttle(() => {
            if (this.ui.isNearBottom()) {
                this.loadMoreProducts();
            }
        }, 200));
    }

    /**
     * Инициализация Intersection Observer для ленивой загрузки
     */
    initIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    /**
     * Инициализация Service Worker для кэширования
     */
    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker зарегистрирован');
            } catch (error) {
                console.log('Service Worker не удалось зарегистрировать:', error);
            }
        }
    }

    /**
     * Загрузка дополнительных товаров
     */
    async loadMoreProducts() {
        if (this.ui.isLoading) return;
        
        this.ui.showLoadingSpinner();
        
        try {
            const response = await fetch('/api/products/load-more', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page: this.ui.currentPage + 1,
                    filters: this.filters.getActiveFilters()
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.ui.appendProducts(data.products);
                this.ui.currentPage++;
            }
        } catch (error) {
            console.error('Ошибка загрузки товаров:', error);
            this.notifications.show('Ошибка загрузки товаров', 'error');
        } finally {
            this.ui.hideLoadingSpinner();
        }
    }
}

/**
 * Менеджер корзины
 */
class CartManager {
    constructor() {
        this.items = this.loadFromStorage();
        this.apiEndpoint = '/api/cart';
    }

    init() {
        this.updateCartBadge();
        this.bindCartEvents();
    }

    /**
     * Добавление товара в корзину
     */
    async addItem(productId, quantity = 1) {
        try {
            const response = await fetch(`${this.apiEndpoint}/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_id: productId, quantity })
            });

            const data = await response.json();

            if (data.success) {
                this.items.push({ productId, quantity });
                this.saveToStorage();
                this.updateCartBadge();
                this.showCartAnimation(productId);
                app.notifications.show('Товар добавлен в корзину!', 'success');
            } else {
                app.notifications.show(data.error || 'Ошибка добавления товара', 'error');
            }
        } catch (error) {
            console.error('Ошибка добавления в корзину:', error);
            app.notifications.show('Ошибка сети', 'error');
        }
    }

    /**
     * Обновление количества товара
     */
    async updateQuantity(productId, quantity) {
        try {
            const response = await fetch(`${this.apiEndpoint}/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_id: productId, quantity })
            });

            const data = await response.json();

            if (data.success) {
                const item = this.items.find(item => item.productId === productId);
                if (item) {
                    item.quantity = quantity;
                    this.saveToStorage();
                    this.updateCartBadge();
                }
            }
        } catch (error) {
            console.error('Ошибка обновления корзины:', error);
        }
    }

    /**
     * Удаление товара из корзины
     */
    async removeItem(productId) {
        try {
            const response = await fetch(`${this.apiEndpoint}/remove`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_id: productId })
            });

            const data = await response.json();

            if (data.success) {
                this.items = this.items.filter(item => item.productId !== productId);
                this.saveToStorage();
                this.updateCartBadge();
                app.notifications.show('Товар удален из корзины', 'info');
            }
        } catch (error) {
            console.error('Ошибка удаления из корзины:', error);
        }
    }

    /**
     * Анимация добавления в корзину
     */
    showCartAnimation(productId) {
        const productCard = document.querySelector(`[data-product-id="${productId}"]`);
        const cartIcon = document.querySelector('.cart-icon');
        
        if (productCard && cartIcon) {
            const productImg = productCard.querySelector('.product-image');
            const flyingImg = productImg.cloneNode(true);
            
            // Стили для летящего изображения
            flyingImg.style.position = 'fixed';
            flyingImg.style.zIndex = '9999';
            flyingImg.style.width = '60px';
            flyingImg.style.height = '60px';
            flyingImg.style.borderRadius = '50%';
            flyingImg.style.transition = 'all 0.8s cubic-bezier(0.2, 1, 0.3, 1)';
            flyingImg.style.pointerEvents = 'none';
            
            const productRect = productImg.getBoundingClientRect();
            const cartRect = cartIcon.getBoundingClientRect();
            
            flyingImg.style.left = `${productRect.left}px`;
            flyingImg.style.top = `${productRect.top}px`;
            
            document.body.appendChild(flyingImg);
            
            // Запуск анимации
            requestAnimationFrame(() => {
                flyingImg.style.left = `${cartRect.left}px`;
                flyingImg.style.top = `${cartRect.top}px`;
                flyingImg.style.transform = 'scale(0.3)';
                flyingImg.style.opacity = '0.7';
            });
            
            // Удаление после анимации
            setTimeout(() => {
                flyingImg.remove();
                cartIcon.style.animation = 'bounce 0.5s ease';
                setTimeout(() => {
                    cartIcon.style.animation = '';
                }, 500);
            }, 800);
        }
    }

    /**
     * Привязка событий корзины
     */
    bindCartEvents() {
        // Количество товаров
        document.addEventListener('click', (e) => {
            if (e.target.matches('.quantity-increase')) {
                const productId = e.target.dataset.productId;
                const input = e.target.parentNode.querySelector('.quantity-input');
                const newQuantity = parseInt(input.value) + 1;
                input.value = newQuantity;
                this.updateQuantity(productId, newQuantity);
            }

            if (e.target.matches('.quantity-decrease')) {
                const productId = e.target.dataset.productId;
                const input = e.target.parentNode.querySelector('.quantity-input');
                const newQuantity = Math.max(1, parseInt(input.value) - 1);
                input.value = newQuantity;
                this.updateQuantity(productId, newQuantity);
            }

            if (e.target.matches('.remove-from-cart')) {
                const productId = e.target.dataset.productId;
                this.removeItem(productId);
            }
        });

        // Прямое изменение количества
        document.addEventListener('change', (e) => {
            if (e.target.matches('.quantity-input')) {
                const productId = e.target.dataset.productId;
                const quantity = Math.max(1, parseInt(e.target.value) || 1);
                e.target.value = quantity;
                this.updateQuantity(productId, quantity);
            }
        });
    }

    /**
     * Обновление значка корзины
     */
    updateCartBadge() {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
            badge.textContent = totalItems;
            badge.style.display = totalItems > 0 ? 'flex' : 'none';
        }
    }

    /**
     * Сохранение в localStorage
     */
    saveToStorage() {
        localStorage.setItem('shein-cart', JSON.stringify(this.items));
    }

    /**
     * Загрузка из localStorage
     */
    loadFromStorage() {
        try {
            return JSON.parse(localStorage.getItem('shein-cart')) || [];
        } catch {
            return [];
        }
    }
}

/**
 * Менеджер уведомлений
 */
class NotificationManager {
    constructor() {
        this.container = this.createContainer();
    }

    /**
     * Создание контейнера для уведомлений
     */
    createContainer() {
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Показ уведомления
     */
    show(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);

        // Анимация появления
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        });

        // Автоматическое скрытие
        setTimeout(() => {
            this.hide(notification);
        }, duration);

        return notification;
    }

    /**
     * Создание уведомления
     */
    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const colors = {
            success: { bg: '#d4edda', border: '#c3e6cb', text: '#155724' },
            error: { bg: '#f8d7da', border: '#f5c6cb', text: '#721c24' },
            warning: { bg: '#fff3cd', border: '#ffeaa7', text: '#856404' },
            info: { bg: '#d1ecf1', border: '#bee5eb', text: '#0c5460' }
        };

        const color = colors[type] || colors.info;

        notification.style.cssText = `
            background: ${color.bg};
            color: ${color.text};
            border: 1px solid ${color.border};
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            max-width: 400px;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.2, 1, 0.3, 1);
            pointer-events: auto;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 500;
        `;

        notification.innerHTML = `
            <span style="font-size: 18px;">${icons[type] || icons.info}</span>
            <span>${message}</span>
            <button style="
                margin-left: auto;
                background: none;
                border: none;
                color: currentColor;
                cursor: pointer;
                opacity: 0.7;
                font-size: 20px;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">×</button>
        `;

        // Закрытие по клику
        notification.addEventListener('click', () => this.hide(notification));

        return notification;
    }

    /**
     * Скрытие уведомления
     */
    hide(notification) {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

/**
 * Менеджер поиска
 */
class SearchManager {
    constructor() {
        this.debounceTimeout = null;
        this.cache = new Map();
    }

    /**
     * Обработка отправки формы поиска
     */
    handleSearch(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const query = formData.get('q');
        const category = formData.get('category');
        
        const url = new URL('/search', window.location.origin);
        if (query) url.searchParams.set('q', query);
        if (category) url.searchParams.set('category', category);
        
        window.location.href = url.toString();
    }

    /**
     * Быстрый поиск с автодополнением
     */
    async quickSearch(query) {
        if (!query || query.length < 2) {
            this.hideSearchSuggestions();
            return;
        }

        // Проверка кэша
        if (this.cache.has(query)) {
            this.showSearchSuggestions(this.cache.get(query));
            return;
        }

        try {
            const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const suggestions = await response.json();
                this.cache.set(query, suggestions);
                this.showSearchSuggestions(suggestions);
            }
        } catch (error) {
            console.error('Ошибка поиска:', error);
        }
    }

    /**
     * Показ подсказок поиска
     */
    showSearchSuggestions(suggestions) {
        let container = document.querySelector('.search-suggestions');
        if (!container) {
            container = document.createElement('div');
            container.className = 'search-suggestions';
            container.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                z-index: 1000;
                max-height: 300px;
                overflow-y: auto;
                margin-top: 4px;
            `;
            
            const searchContainer = document.querySelector('.search-container');
            if (searchContainer) {
                searchContainer.style.position = 'relative';
                searchContainer.appendChild(container);
            }
        }

        container.innerHTML = suggestions.map(item => `
            <div class="search-suggestion" style="
                padding: 12px 16px;
                cursor: pointer;
                border-bottom: 1px solid #f3f4f6;
                transition: background-color 0.2s;
                display: flex;
                align-items: center;
                gap: 12px;
            " data-query="${item.name}">
                <img src="${item.image}" alt="${item.name}" style="
                    width: 40px;
                    height: 40px;
                    object-fit: cover;
                    border-radius: 8px;
                ">
                <div>
                    <div style="font-weight: 500; color: #374151;">${item.name}</div>
                    <div style="font-size: 12px; color: #6b7280;">${item.category}</div>
                </div>
                <div style="margin-left: auto; font-weight: 600; color: #f97316;">$${item.price}</div>
            </div>
        `).join('');

        // Обработка кликов по подсказкам
        container.addEventListener('click', (e) => {
            const suggestion = e.target.closest('.search-suggestion');
            if (suggestion) {
                const query = suggestion.dataset.query;
                document.querySelector('#search-input').value = query;
                this.hideSearchSuggestions();
                document.querySelector('.search-form').dispatchEvent(new Event('submit'));
            }
        });

        // Стили при наведении
        container.addEventListener('mouseover', (e) => {
            const suggestion = e.target.closest('.search-suggestion');
            if (suggestion) {
                suggestion.style.backgroundColor = '#f9fafb';
            }
        });

        container.addEventListener('mouseout', (e) => {
            const suggestion = e.target.closest('.search-suggestion');
            if (suggestion) {
                suggestion.style.backgroundColor = 'white';
            }
        });
    }

    /**
     * Скрытие подсказок поиска
     */
    hideSearchSuggestions() {
        const container = document.querySelector('.search-suggestions');
        if (container) {
            container.remove();
        }
    }
}

/**
 * Менеджер списка желаний
 */
class WishlistManager {
    constructor() {
        this.items = this.loadFromStorage();
    }

    /**
     * Переключение товара в списке желаний
     */
    toggleItem(productId) {
        const index = this.items.indexOf(productId);
        
        if (index > -1) {
            this.items.splice(index, 1);
            app.notifications.show('Товар удален из избранного', 'info');
        } else {
            this.items.push(productId);
            app.notifications.show('Товар добавлен в избранное!', 'success');
        }
        
        this.saveToStorage();
        this.updateWishlistButtons();
    }

    /**
     * Обновление кнопок списка желаний
     */
    updateWishlistButtons() {
        document.querySelectorAll('.wishlist-btn').forEach(btn => {
            const productId = btn.dataset.productId;
            const isInWishlist = this.items.includes(productId);
            
            btn.innerHTML = isInWishlist ? '❤️' : '🤍';
            btn.classList.toggle('active', isInWishlist);
        });
    }

    /**
     * Сохранение в localStorage
     */
    saveToStorage() {
        localStorage.setItem('shein-wishlist', JSON.stringify(this.items));
    }

    /**
     * Загрузка из localStorage
     */
    loadFromStorage() {
        try {
            return JSON.parse(localStorage.getItem('shein-wishlist')) || [];
        } catch {
            return [];
        }
    }
}

/**
 * Менеджер фильтров
 */
class FilterManager {
    constructor() {
        this.filters = {};
    }

    /**
     * Применение фильтров
     */
    applyFilters() {
        this.updateFilters();
        const products = document.querySelectorAll('.product-card');
        
        products.forEach(product => {
            const shouldShow = this.matchesFilters(product);
            product.style.display = shouldShow ? 'block' : 'none';
        });

        this.updateResultsCount();
    }

    /**
     * Обновление объекта фильтров
     */
    updateFilters() {
        this.filters = {};
        
        document.querySelectorAll('.filter-input').forEach(input => {
            if (input.checked || (input.type === 'range' && input.value)) {
                const filterType = input.dataset.filterType;
                const filterValue = input.value;
                
                if (!this.filters[filterType]) {
                    this.filters[filterType] = [];
                }
                this.filters[filterType].push(filterValue);
            }
        });
    }

    /**
     * Проверка соответствия товара фильтрам
     */
    matchesFilters(productElement) {
        for (const [filterType, values] of Object.entries(this.filters)) {
            const productValue = productElement.dataset[filterType];
            
            if (filterType === 'price') {
                const price = parseFloat(productElement.dataset.price);
                const [min, max] = values[0].split('-').map(Number);
                if (price < min || price > max) return false;
            } else {
                if (!values.includes(productValue)) return false;
            }
        }
        return true;
    }

    /**
     * Получение активных фильтров
     */
    getActiveFilters() {
        return this.filters;
    }

    /**
     * Обновление счетчика результатов
     */
    updateResultsCount() {
        const visibleProducts = document.querySelectorAll('.product-card:not([style*="display: none"])');
        const counter = document.querySelector('.results-count');
        
        if (counter) {
            counter.textContent = `Найдено товаров: ${visibleProducts.length}`;
        }
    }
}

/**
 * Менеджер UI
 */
class UIManager {
    constructor() {
        this.isLoading = false;
        this.currentPage = 1;
    }

    init() {
        this.initLazyLoading();
        this.initScrollToTop();
        this.initTooltips();
        this.initModals();
    }

    /**
     * Throttle функция для оптимизации производительности
     */
    throttle(func, delay) {
        let timeoutId;
        let lastExecTime = 0;
        return function (...args) {
            const currentTime = Date.now();
            
            if (currentTime - lastExecTime > delay) {
                func.apply(this, args);
                lastExecTime = currentTime;
            } else {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    func.apply(this, args);
                    lastExecTime = Date.now();
                }, delay - (currentTime - lastExecTime));
            }
        };
    }

    /**
     * Проверка близости к нижней части страницы
     */
    isNearBottom(threshold = 200) {
        return window.innerHeight + window.scrollY >= document.body.offsetHeight - threshold;
    }

    /**
     * Показ спиннера загрузки
     */
    showLoadingSpinner() {
        this.isLoading = true;
        let spinner = document.querySelector('.loading-spinner-main');
        
        if (!spinner) {
            spinner = document.createElement('div');
            spinner.className = 'loading-spinner-main';
            spinner.innerHTML = `
                <div style="
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: white;
                    padding: 20px;
                    border-radius: 50%;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    z-index: 1000;
                ">
                    <div class="loading-spinner"></div>
                </div>
            `;
            document.body.appendChild(spinner);
        }
        
        spinner.style.display = 'block';
    }

    /**
     * Скрытие спиннера загрузки
     */
    hideLoadingSpinner() {
        this.isLoading = false;
        const spinner = document.querySelector('.loading-spinner-main');
        if (spinner) {
            spinner.style.display = 'none';
        }
    }

    /**
     * Добавление товаров на страницу
     */
    appendProducts(products) {
        const container = document.querySelector('.products-grid');
        if (!container) return;

        products.forEach(product => {
            const productHTML = this.createProductCard(product);
            container.insertAdjacentHTML('beforeend', productHTML);
        });

        // Обновление ленивой загрузки для новых изображений
        this.initLazyLoading();
    }

    /**
     * Создание карточки товара
     */
    createProductCard(product) {
        const discountedPrice = product.price * (1 - product.discount / 100);
        
        return `
            <div class="product-card animate-fadeInUp" data-product-id="${product.id}" data-price="${discountedPrice}" data-category="${product.category}">
                <div class="product-image-container">
                    <img class="product-image lazy" data-src="${product.image}" alt="${product.name}">
                    ${product.discount > 0 ? `<div class="product-badge">-${product.discount}%</div>` : ''}
                    <button class="product-wishlist wishlist-btn" data-product-id="${product.id}">🤍</button>
                </div>
                <div class="product-info">
                    <div class="product-category">${product.category}</div>
                    <h3 class="product-title">${product.name}</h3>
                    <div class="product-rating">
                        <div class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</div>
                        <span class="rating-text">(${product.reviews_count || 0})</span>
                    </div>
                    <div class="product-price">
                        <span class="current-price">$${discountedPrice.toFixed(2)}</span>
                        ${product.discount > 0 ? `<span class="original-price">$${product.price.toFixed(2)}</span>` : ''}
                        ${product.discount > 0 ? `<span class="discount-badge">-${product.discount}%</span>` : ''}
                    </div>
                    <div class="product-actions">
                        <button class="add-to-cart-btn" data-product-id="${product.id}">
                            <i class="fas fa-shopping-cart"></i>
                            В корзину
                        </button>
                        <button class="quick-view-btn" data-product-id="${product.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Инициализация ленивой загрузки
     */
    initLazyLoading() {
        const lazyImages = document.querySelectorAll('img.lazy');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });

            lazyImages.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback для старых браузеров
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
            });
        }
    }

    /**
     * Инициализация кнопки "Наверх"
     */
    initScrollToTop() {
        const scrollBtn = document.createElement('button');
        scrollBtn.className = 'scroll-to-top';
        scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 50px;
            height: 50px;
            background: var(--gradient-primary);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        document.body.appendChild(scrollBtn);

        // Показ/скрытие кнопки при прокрутке
        window.addEventListener('scroll', this.throttle(() => {
            if (window.pageYOffset > 300) {
                scrollBtn.style.opacity = '1';
                scrollBtn.style.visibility = 'visible';
            } else {
                scrollBtn.style.opacity = '0';
                scrollBtn.style.visibility = 'hidden';
            }
        }, 100));

        // Плавная прокрутка наверх
        scrollBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    /**
     * Инициализация подсказок
     */
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            let tooltip;
            
            element.addEventListener('mouseenter', (e) => {
                tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = e.target.dataset.tooltip;
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    z-index: 10000;
                    pointer-events: none;
                    white-space: nowrap;
                    opacity: 0;
                    transition: opacity 0.2s;
                `;
                
                document.body.appendChild(tooltip);
                
                const rect = e.target.getBoundingClientRect();
                tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
                
                setTimeout(() => {
                    tooltip.style.opacity = '1';
                }, 100);
            });
            
            element.addEventListener('mouseleave', () => {
                if (tooltip) {
                    tooltip.remove();
                }
            });
        });
    }

    /**
     * Инициализация модальных окон
     */
    initModals() {
        // Закрытие модальных окон по клику на фон
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Закрытие по клавише Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    this.closeModal(openModal);
                }
            }
        });
    }

    /**
     * Показ быстрого просмотра товара
     */
    async showQuickView(productId) {
        try {
            const response = await fetch(`/api/product/${productId}`);
            if (response.ok) {
                const product = await response.json();
                this.createQuickViewModal(product);
            }
        } catch (error) {
            console.error('Ошибка загрузки товара:', error);
            app.notifications.show('Ошибка загрузки товара', 'error');
        }
    }

    /**
     * Создание модального окна быстрого просмотра
     */
    createQuickViewModal(product) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px;">
                <div class="modal-header">
                    <h3 class="modal-title">${product.name}</h3>
                    <button class="btn-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <img src="${product.image}" alt="${product.name}" class="img-fluid rounded">
                        </div>
                        <div class="col-md-6">
                            <div class="product-rating mb-3">
                                <div class="stars">${'★'.repeat(Math.floor(product.rating))}${'☆'.repeat(5 - Math.floor(product.rating))}</div>
                                <span class="rating-text">(${product.reviews_count || 0} отзывов)</span>
                            </div>
                            <div class="product-price mb-3">
                                <span class="current-price">$${(product.price * (1 - product.discount / 100)).toFixed(2)}</span>
                                ${product.discount > 0 ? `<span class="original-price">$${product.price.toFixed(2)}</span>` : ''}
                            </div>
                            <p class="mb-3">${product.description}</p>
                            <div class="mb-3">
                                <label class="form-label">Количество:</label>
                                <div class="quantity-controls">
                                    <button class="quantity-btn" onclick="this.nextElementSibling.stepDown()">-</button>
                                    <input type="number" class="quantity-input" value="1" min="1">
                                    <button class="quantity-btn" onclick="this.previousElementSibling.stepUp()">+</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="app.ui.closeModal(this.closest('.modal'))">Закрыть</button>
                    <button class="btn btn-primary" onclick="app.cart.addItem('${product.id}', parseInt(this.closest('.modal').querySelector('.quantity-input').value))">Добавить в корзину</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 100);

        // Обработка закрытия
        modal.querySelector('.btn-close').addEventListener('click', () => this.closeModal(modal));
    }

    /**
     * Закрытие модального окна
     */
    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }
}

// Инициализация приложения
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SheinMarket();
});

// Экспорт для использования в других файлах
window.SheinMarket = SheinMarket;

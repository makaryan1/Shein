
// Service Worker для кэширования ресурсов
const CACHE_NAME = 'shein-market-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/favicon.ico'
];

// Установка Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Перехват запросов
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Возвращаем кэшированную версию или делаем запрос к серверу
                return response || fetch(event.request);
            }
        )
    );
});

// Активация нового Service Worker
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

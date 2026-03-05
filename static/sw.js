const CACHE_NAME = 'glow-saju-v3';
const ASSETS = [
    '/',
    '/static/style.css',
    '/static/icon.png',
    '/static/manifest.json',
    'https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => response || fetch(event.request))
    );
});

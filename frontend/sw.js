/**
 * Service Worker for EPD-Hub
 * Enables offline functionality and caching strategies
 */

const CACHE_NAME = 'epd-hub-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/css/styles.css',
    '/css/responsive.css',
    '/js/main.js'
];

/**
 * Install event - cache essential assets
 */
self.addEventListener('install', event => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('Service Worker: Caching essential assets');
            return cache.addAll(ASSETS_TO_CACHE).catch(err => {
                console.error('Service Worker: Cache failed', err);
                // Continue even if some assets can't be cached
            });
        })
    );
    
    self.skipWaiting();
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    
    self.clients.claim();
});

/**
 * Fetch event - serve from cache, fall back to network
 */
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip cross-origin requests
    if (url.origin !== location.origin) {
        return;
    }

    // Use cache-first strategy for static assets
    if (request.method === 'GET' && (
        request.url.includes('/css/') ||
        request.url.includes('/js/') ||
        request.url.includes('/assets/')
    )) {
        event.respondWith(
            caches.match(request).then(response => {
                return response || fetch(request).then(response => {
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }
                    
                    const responseToCache = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(request, responseToCache);
                    });
                    
                    return response;
                });
            }).catch(() => {
                // Return a fallback response if offline
                return caches.match('/index.html');
            })
        );
        return;
    }

    // Use network-first strategy for API requests
    if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
        event.respondWith(
            fetch(request)
                .then(response => {
                    if (response.status === 200 && request.method === 'GET') {
                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(request, responseToCache);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    return caches.match(request).then(response => {
                        return response || new Response(
                            JSON.stringify({ error: 'Offline - API unavailable' }),
                            { status: 503, statusText: 'Service Unavailable' }
                        );
                    });
                })
        );
        return;
    }

    // Default strategy: network first, cache fallback
    event.respondWith(
        fetch(request)
            .then(response => {
                return response;
            })
            .catch(() => {
                return caches.match(request).then(response => {
                    return response || caches.match('/index.html');
                });
            })
    );
});

/**
 * Message event - handle communication from clients
 */
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

console.log('Service Worker loaded and ready');

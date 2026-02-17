const CACHE_NAME = 'home-needs-v1.0.0';
const OFFLINE_URL = '/login';

const PRECACHE_URLS = [
    '/',
    '/login',
    '/signup',
    '/dashboard',
    '/vegfruits-procure',
    '/groceries-procure',
    '/vegfruits-list',
    '/groceries-list',
    '/static/css/style.css',
    '/static/js/app.js',
    '/manifest.json',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
];

// Install — cache core assets
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('[SW] Pre-caching core assets');
                return cache.addAll(PRECACHE_URLS);
            })
            .then(function() {
                return self.skipWaiting();
            })
            .catch(function(err) {
                console.log('[SW] Pre-cache failed:', err);
            })
    );
});

// Activate — clean old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys()
            .then(function(cacheNames) {
                return Promise.all(
                    cacheNames
                        .filter(function(name) { return name !== CACHE_NAME; })
                        .map(function(name) {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(function() {
                return self.clients.claim();
            })
    );
});

// Fetch — network first for API, cache first for assets
self.addEventListener('fetch', function(event) {
    var request = event.request;
    var url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // API calls — network only (always fresh data)
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .catch(function() {
                    return new Response(
                        JSON.stringify({ success: false, message: 'You are offline' }),
                        { headers: { 'Content-Type': 'application/json' } }
                    );
                })
        );
        return;
    }
    
    // Auth routes — network first
    if (url.pathname === '/login' || url.pathname === '/signup' || 
        url.pathname === '/verify' || url.pathname === '/logout') {
        event.respondWith(
            fetch(request)
                .then(function(response) {
                    var responseClone = response.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(request, responseClone);
                    });
                    return response;
                })
                .catch(function() {
                    return caches.match(request);
                })
        );
        return;
    }
    
    // Static assets — cache first
    if (url.pathname.startsWith('/static/') || 
        url.hostname === 'fonts.googleapis.com' ||
        url.hostname === 'fonts.gstatic.com' ||
        url.hostname === 'cdnjs.cloudflare.com') {
        event.respondWith(
            caches.match(request)
                .then(function(cachedResponse) {
                    if (cachedResponse) {
                        // Update cache in background
                        fetch(request).then(function(networkResponse) {
                            caches.open(CACHE_NAME).then(function(cache) {
                                cache.put(request, networkResponse);
                            });
                        }).catch(function() {});
                        return cachedResponse;
                    }
                    return fetch(request).then(function(response) {
                        var responseClone = response.clone();
                        caches.open(CACHE_NAME).then(function(cache) {
                            cache.put(request, responseClone);
                        });
                        return response;
                    });
                })
        );
        return;
    }
    
    // Pages — network first, fallback to cache
    event.respondWith(
        fetch(request)
            .then(function(response) {
                var responseClone = response.clone();
                caches.open(CACHE_NAME).then(function(cache) {
                    cache.put(request, responseClone);
                });
                return response;
            })
            .catch(function() {
                return caches.match(request)
                    .then(function(cachedResponse) {
                        return cachedResponse || caches.match(OFFLINE_URL);
                    });
            })
    );
});
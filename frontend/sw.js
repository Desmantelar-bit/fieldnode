const CACHE_NAME = 'fieldnode-v1.0.0';
const STATIC_CACHE = 'fieldnode-static-v1.0.0';

// Assets to cache for offline functionality
const STATIC_ASSETS = [
  '/frontend/',
  '/frontend/dashboard.html',
  '/frontend/index.html',
  '/frontend/colheitadeiras.html',
  '/frontend/operarios.html',
  '/frontend/cadastro.html',
  '/frontend/detalhes.html',
  '/frontend/styles.css',
  '/frontend/config.js',
  '/frontend/js/api.js',
  '/frontend/js/colors.js',
  '/frontend/js/status.js',
  '/frontend/manifest.json',
  // CDN resources
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch((error) => {
        console.error('[SW] Failed to cache static assets:', error);
      })
  );
  
  // Force activation of new service worker
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  // Take control of all clients
  self.clients.claim();
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful API responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Return cached API response if available
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              console.log('[SW] Serving cached API response for:', request.url);
              return cachedResponse;
            }
            
            // Return offline fallback for API requests
            return new Response(
              JSON.stringify({
                status: 'offline',
                message: 'Dados em cache não disponíveis. Conecte-se à internet.',
                cached: false
              }),
              {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' }
              }
            );
          });
        })
    );
    return;
  }
  
  // Handle static assets
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        return fetch(request)
          .then((response) => {
            // Cache successful responses
            if (response.ok && request.method === 'GET') {
              const responseClone = response.clone();
              caches.open(STATIC_CACHE).then((cache) => {
                cache.put(request, responseClone);
              });
            }
            return response;
          })
          .catch(() => {
            // Return offline page for navigation requests
            if (request.mode === 'navigate') {
              return caches.match('/frontend/dashboard.html');
            }
            
            // Return empty response for other failed requests
            return new Response('', { status: 404 });
          });
      })
  );
});

// Background sync for when connection is restored
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'telemetria-sync') {
    event.waitUntil(syncTelemetriaData());
  }
});

// Sync telemetria data when online
async function syncTelemetriaData() {
  try {
    // This would sync any offline telemetria data
    // For now, just log that sync is available
    console.log('[SW] Telemetria sync completed');
  } catch (error) {
    console.error('[SW] Telemetria sync failed:', error);
  }
}

// Push notification handling (for future use)
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  const options = {
    body: 'Nova telemetria disponível',
    icon: '/frontend/icons/icon-192x192.png',
    badge: '/frontend/icons/icon-72x72.png',
    tag: 'fieldnode-notification',
    requireInteraction: false,
    actions: [
      {
        action: 'view',
        title: 'Ver Dashboard'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('FieldNode', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/frontend/dashboard.html')
    );
  }
});
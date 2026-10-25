/**
 * SheCare AI / SurvivorCare AI - Offline-First Service Worker
 * Ensures full caching and offline operation without network connectivity.
 * Implements safe MIME fallbacks for static hosting (GitHub Pages).
 */
const CACHE_NAME = 'shecare-v2.4';
const STATIC_ASSETS = [
  './',
  './index.html',
  './css/styles.css',
  './js/db.js',
  './js/auth.js',
  './js/mental_health.js',
  './js/physical_health.js',
  './js/period_tracker.js',
  './js/pregnancy_sti.js',
  './js/sos.js',
  './js/safety_plan.js',
  './js/agency_reporting.js',
  './js/nearby_places.js',
  './css/safe_places.css',
  './js/app.js',
  './manifest.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // Precache static assets gracefully without aborting if an asset is not found
      for (const asset of STATIC_ASSETS) {
        try {
          await cache.add(asset);
        } catch (err) {
          console.warn('[Service Worker] Optional precache skipped for:', asset);
        }
      }
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[Service Worker] Evicting legacy cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  const req = e.request;

  // Only handle same-origin GET requests. Third-party services (maps, geocoding, Overpass)
  // and POSTs must reach the network untouched - never answer them from here.
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // 1. Local backend API: pass through, or give a clean offline JSON response
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(req).catch(() => {
        return new Response(JSON.stringify({
          error: 'Offline / Static Hosting Mode: Backend server is not running on this domain.',
          offline: true
        }), {
          status: 503,
          headers: { 'Content-Type': 'application/json; charset=utf-8' }
        });
      })
    );
    return;
  }

  // 2. Network-first for app files, so an update is always picked up when online
  //    (cache-first kept serving stale HTML/JS that no longer matched each other).
  //    The cache is the offline fallback.
  e.respondWith(
    fetch(req).then((networkResponse) => {
      if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, responseToCache)).catch(() => {});
      }
      return networkResponse;
    }).catch(() => {
      return caches.match(req, { ignoreSearch: true }).then((cachedResponse) => {
        if (cachedResponse) return cachedResponse;
        // ONLY fall back to index.html for page navigation, NEVER for CSS or JS!
        const accept = e.request.headers.get('accept') || '';
        if (e.request.mode === 'navigate' || accept.includes('text/html')) {
          return caches.match('./index.html')
            .then((page) => page || caches.match('./'))
            .then((page) => page || new Response('Offline', { status: 503, statusText: 'Offline' }));
        }
        // Return 404 response instead of breaking MIME types
        return new Response('Asset unavailable offline', { status: 404, statusText: 'Not Found' });
      });
    })
  );
});

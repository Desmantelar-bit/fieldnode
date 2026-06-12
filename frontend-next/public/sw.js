const CACHE_NAME = 'fieldnode-runtime-v2';
const STATIC_CACHE = 'fieldnode-static-v2';
const TELEMETRY_SYNC_TAG = 'fieldnode-telemetria-sync';
const DB_NAME = 'fieldnode-offline';
const DB_VERSION = 1;
const TELEMETRY_STORE = 'telemetria-pendente';

let apiConfig = {
  apiUrl: 'http://127.0.0.1:8000/api',
  apiKey: '',
};

const PRECACHE_URLS = ["/", "/manifest.json", "/icon-192.png", "/icon-512.png"];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)),
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      caches.keys().then((cacheNames) =>
        Promise.all(
          cacheNames
            .filter((cacheName) => ![CACHE_NAME, STATIC_CACHE].includes(cacheName))
            .map((cacheName) => caches.delete(cacheName))
        )
      ),
      self.clients.claim(),
    ])
  );
});

self.addEventListener('message', (event) => {
  const message = event.data || {};

  if (message.type === 'FIELDNODE_CONFIG') {
    apiConfig = {
      apiUrl: normalizeApiUrl(message.apiUrl || apiConfig.apiUrl),
      apiKey: message.apiKey || apiConfig.apiKey,
    };
    return;
  }

  if (message.type === 'QUEUE_TELEMETRY') {
    event.waitUntil(queueTelemetry(message.payload, message.headers || {}).then(requestSync));
  }
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  if (isTelemetryPost(request)) {
    event.respondWith(sendOrQueueTelemetry(request));
    return;
  }

  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  event.respondWith(cacheFirst(request));
});

self.addEventListener('sync', (event) => {
  if (event.tag === TELEMETRY_SYNC_TAG) {
    event.waitUntil(syncTelemetriaData());
  }
});

async function sendOrQueueTelemetry(request) {
  const requestForNetwork = request.clone();
  const requestForQueue = request.clone();

  try {
    const response = await fetch(requestForNetwork);
    if (!response.ok && shouldRetryStatus(response.status)) {
      await queueRequest(requestForQueue);
      await requestSync();
      return queuedResponse('Backend indisponivel. Leitura guardada para reenvio.');
    }
    return response;
  } catch {
    await queueRequest(requestForQueue);
    await requestSync();
    return queuedResponse('Sem conexao. Leitura guardada para reenvio.');
  }
}

async function syncTelemetriaData() {
  const db = await openDb();
  const items = await readAll(db);

  for (const item of items) {
    const response = await fetch(item.url || `${apiConfig.apiUrl}/telemetria/`, {
      method: 'POST',
      headers: buildHeaders(item.headers),
      body: JSON.stringify(item.payload),
    });

    if (response.ok || response.status === 400 || response.status === 401) {
      await deleteItem(db, item.localId);
      continue;
    }

    throw new Error(`HTTP ${response.status}`);
  }

  await notifyClients({ type: 'TELEMETRY_SYNCED', count: items.length });
}

async function queueRequest(request) {
  const payload = await request.json();
  const headers = {};
  request.headers.forEach((value, key) => {
    headers[key] = value;
  });
  await queueTelemetry(payload, headers, request.url);
}

async function queueTelemetry(payload, headers = {}, url = `${apiConfig.apiUrl}/telemetria/`) {
  const db = await openDb();
  const item = {
    localId: crypto.randomUUID(),
    payload,
    headers,
    url,
    createdAt: new Date().toISOString(),
  };
  await putItem(db, item);
  await notifyClients({ type: 'TELEMETRY_QUEUED', localId: item.localId });
}

function isTelemetryPost(request) {
  if (request.method !== 'POST') return false;

  const url = new URL(request.url);
  const apiUrl = new URL(apiConfig.apiUrl);
  const apiTelemetryPath = `${apiUrl.pathname.replace(/\/$/, '')}/telemetria/`;
  const isSameApiHost = url.origin === apiUrl.origin && url.pathname === apiTelemetryPath;
  const isProxiedApi = url.pathname === '/api/telemetria/';

  return isSameApiHost || isProxiedApi;
}

async function requestSync() {
  if ('sync' in self.registration) {
    await self.registration.sync.register(TELEMETRY_SYNC_TAG);
    return;
  }

  if (navigator.onLine) {
    syncTelemetriaData().catch((error) => {
      console.error('[SW] Telemetria sync failed:', error);
    });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      await cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || jsonResponse({ status: 'offline', message: 'Dados em cache nao disponiveis.' }, 503);
  }
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      await cache.put(request, response.clone());
    }
    return response;
  } catch {
    if (request.mode === 'navigate') {
      return caches.match('/dashboard') || caches.match('/');
    }
    return new Response('', { status: 404 });
  }
}

function buildHeaders(headers) {
  return {
    ...headers,
    Accept: 'application/json',
    'Content-Type': 'application/json',
    ...(apiConfig.apiKey ? { 'X-API-Key': apiConfig.apiKey } : {}),
  };
}

function queuedResponse(message) {
  return jsonResponse({ status: 'queued', message, offline: true }, 202);
}

function jsonResponse(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function shouldRetryStatus(status) {
  return status === 408 || status === 429 || status >= 500;
}

function normalizeApiUrl(value) {
  return String(value || '').replace(/\/$/, '');
}

function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(TELEMETRY_STORE)) {
        db.createObjectStore(TELEMETRY_STORE, { keyPath: 'localId' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function readAll(db) {
  return tx(db, 'readonly', (store) => store.getAll());
}

function putItem(db, item) {
  return tx(db, 'readwrite', (store) => store.put(item));
}

function deleteItem(db, key) {
  return tx(db, 'readwrite', (store) => store.delete(key));
}

function tx(db, mode, action) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(TELEMETRY_STORE, mode);
    const store = transaction.objectStore(TELEMETRY_STORE);
    const request = action(store);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function notifyClients(message) {
  const clientsList = await self.clients.matchAll({ includeUncontrolled: true });
  clientsList.forEach((client) => client.postMessage(message));
}

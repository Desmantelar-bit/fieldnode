const CACHE_NAME = 'fieldnode-runtime-v3';
const STATIC_CACHE = 'fieldnode-static-v2';
const TELEMETRY_SYNC_TAG = 'fieldnode-telemetria-sync';
const DB_NAME = 'fieldnode-offline';
const DB_VERSION = 1;
const TELEMETRY_STORE = 'telemetria-pendente';
const TELEMETRY_URL = '/api/telemetria/';

const PRECACHE_URLS = ["/manifest.json", "/icon-192.png", "/icon-512.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      caches
        .keys()
        .then((cacheNames) =>
          Promise.all(
            cacheNames
              .filter(
                (cacheName) =>
                  cacheName.startsWith("fieldnode-") &&
                  ![CACHE_NAME, STATIC_CACHE].includes(cacheName),
              )
              .map((cacheName) => caches.delete(cacheName)),
          ),
        ),
      sanitizeQueuedHeaders().catch((error) => {
        console.warn("[SW] Pending telemetry credentials could not be sanitized.", error);
      }),
      self.clients.claim(),
    ]),
  );
});

self.addEventListener("message", (event) => {
  const message = event.data || {};
  if (message.type === "QUEUE_TELEMETRY") {
    event.waitUntil(
      queueTelemetry(message.payload).then(requestSync),
    );
  }
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (isTelemetryPost(request)) {
    event.respondWith(sendOrQueueTelemetry(request));
    return;
  }
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.startsWith("/api/")) {
    event.respondWith(fetch(request));
    return;
  }

  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  event.respondWith(fetch(request));
});

function isStaticAsset(pathname) {
  return (
    pathname.startsWith("/_next/static/") ||
    pathname.startsWith("/brand/") ||
    pathname === "/manifest.json" ||
    pathname === "/favicon.ico" ||
    /^\/icon-\d+\.png$/.test(pathname)
  );
}

 self.addEventListener("sync", (event) => {
  if (event.tag === TELEMETRY_SYNC_TAG) {
    event.waitUntil(syncTelemetriaData());
  }
});

async function sendOrQueueTelemetry(request) {
  const headers = new Headers(request.headers);
  headers.delete("X-API-Key");
  headers.delete("Authorization");
  const safeRequest = new Request(request, { headers });

  try {
    const response = await fetch(safeRequest.clone());
    if (response.status === 408 || response.status === 429 || response.status >= 500) {
      await queueRequest(safeRequest);
      await requestSync();
      return queuedResponse("Backend indisponivel. Leitura guardada para reenvio.");
    }
    return response;
  } catch {
    await queueRequest(safeRequest);
    await requestSync();
    return queuedResponse("Sem conexao. Leitura guardada para reenvio.");
  }
}

async function syncTelemetriaData() {
  const db = await openDb();
  const items = await readAll(db);

  for (const item of items) {
    item.payload = withTelemetryIdentity(item.payload);
    await putItem(db, item);
    const response = await fetch(TELEMETRY_URL, {
      method: "POST",
      headers: buildHeaders(),
      body: JSON.stringify(item.payload),
    });

    if (response.ok) {
      await deleteItem(db, item.localId);
      continue;
    }

    await notifyClients({
      type: "TELEMETRY_SYNC_BLOCKED",
      status: response.status,
      pending: items.length,
    });
    if (response.status === 408 || response.status === 429 || response.status >= 500) {
      throw new Error(`HTTP ${response.status}`);
    }
    return;
  }

  await notifyClients({ type: "TELEMETRY_SYNCED", count: items.length });
}

async function queueRequest(request) {
  const payload = await request.json();
  await queueTelemetry(payload);
}

async function queueTelemetry(payload) {
  const db = await openDb();
  const item = {
    localId: crypto.randomUUID(),
    payload,
    createdAt: new Date().toISOString(),
  };
  await putItem(db, item);
  await notifyClients({ type: "TELEMETRY_QUEUED", localId: item.localId });
}

function isTelemetryPost(request) {
  if (request.method !== "POST") return false;
  const url = new URL(request.url);
  return url.origin === self.location.origin && url.pathname === TELEMETRY_URL;
}

async function requestSync() {
  if ("sync" in self.registration) {
    await self.registration.sync.register(TELEMETRY_SYNC_TAG);
    return;
  }

  if (navigator.onLine) {
    syncTelemetriaData().catch((error) => {
      console.error("[SW] Telemetria sync failed:", error);
    });
  }
}

async function sanitizeQueuedHeaders() {
  const db = await openDb();
  const items = await readAll(db);
  for (const item of items) {
    if (item.headers) {
      delete item.headers["X-API-Key"];
      delete item.headers["x-api-key"];
      delete item.headers.Authorization;
      delete item.headers.authorization;
      delete item.headers["Proxy-Authorization"];
      delete item.headers["proxy-authorization"];
      await putItem(db, item);
    }
  }
}

function buildHeaders() {
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}

function withTelemetryIdentity(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return payload;
  }

  const machineId = typeof payload.maquina_id === "string" ? payload.maquina_id : "";
  return {
    ...payload,
    device_id:
      typeof payload.device_id === "string" && payload.device_id.trim()
        ? payload.device_id
        : machineId.trim().toUpperCase(),
    message_id:
      typeof payload.message_id === "string" && payload.message_id.trim()
        ? payload.message_id
        : typeof payload.id === "string" && payload.id.trim()
          ? payload.id
          : crypto.randomUUID(),
  };
}

function queuedResponse(message) {
  return new Response(JSON.stringify({ status: "queued", message, offline: true }), {
    status: 202,
    headers: { "Content-Type": "application/json" },
  });
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
    return new Response("", { status: 404 });
  }
}

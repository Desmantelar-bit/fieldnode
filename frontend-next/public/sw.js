const CACHE_NAME = 'fieldnode-runtime-v3';
const STATIC_CACHE = 'fieldnode-static-v3';
const TELEMETRY_SYNC_TAG = 'fieldnode-telemetria-sync';
const DB_NAME = 'fieldnode-offline';
const DB_VERSION = 2;
const TELEMETRY_STORE = 'telemetria-pendente';

let apiConfig = {
  apiUrl: "/api",
};
let syncInProgress = false;

const PRECACHE_URLS = ["/", "/manifest.json", "/icon-192.png", "/icon-512.png"];

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
                (cacheName) => ![CACHE_NAME, STATIC_CACHE].includes(cacheName),
              )
              .map((cacheName) => caches.delete(cacheName)),
          ),
        ),
      self.clients.claim(),
    ]),
  );
});

self.addEventListener("message", (event) => {
  const message = event.data || {};

  if (message.type === "FIELDNODE_CONFIG") {
    apiConfig = {
      apiUrl: normalizeApiUrl(message.apiUrl || apiConfig.apiUrl),
    };
    return;
  }

  if (message.type === "CLEAR_PRIVATE_CACHE") {
    event.waitUntil(caches.delete(CACHE_NAME));
    return;
  }

  if (message.type === "QUEUE_TELEMETRY") {
    event.waitUntil(
      queueTelemetry(message.payload, message.headers || {}).then(requestSync),
    );
  }
  if (message.type === "GET_TELEMETRY_STATUS") {
    event.waitUntil(openDb().then(async (db) => notifyClients({ type: "TELEMETRY_QUEUE_STATUS", counts: await countBy(db), items: await queueSummaries(db) })).catch(() => notifyClients({ type: "TELEMETRY_QUEUE_ERROR" })));
  }
  if (message.type === "REPROCESS_REJECTED") {
    event.waitUntil(reprocessRejected().then(requestSync));
  }
  if (message.type === "AUTH_RECOVERED") {
    event.waitUntil(releaseAuthBlocked().then(requestSync));
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
  if (url.pathname.startsWith("/api/")) {
    if (url.pathname.startsWith("/api/auth/")) {
      event.respondWith(fetch(request));
      return;
    }
    event.respondWith(networkFirst(request));
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match("/")),
    );
    return;
  }

  if (isStaticAssetRequest(request)) {
    event.respondWith(cacheFirst(request));
  }
});

self.addEventListener("sync", (event) => {
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
      return queuedResponse(
        "Backend indisponivel. Leitura guardada para reenvio.",
      );
    }
    return response;
  } catch {
    await queueRequest(requestForQueue);
    await requestSync();
    return queuedResponse("Sem conexao. Leitura guardada para reenvio.");
  }
}

async function syncTelemetriaData() {
  if (syncInProgress) return;
  syncInProgress = true;
  let synced = 0;
  try {
  const db = await openDb();
  const now = Date.now();
  const items = (await readAll(db)).filter((item) => {
    normalizeItem(item);
    return item.state !== "rejected" && item.state !== "auth_blocked" && item.next_attempt_at <= now;
  });

  for (const item of items) {
    try {
      const apiUrl = new URL(apiConfig.apiUrl, self.location.origin);
      const response = await fetch(
        item.url || `${apiUrl.toString().replace(/\/$/, "")}/telemetria/`,
        { method: "POST", headers: buildHeaders(item.headers), body: JSON.stringify(item.payload) },
      );
      if (response.ok) {
        await deleteItem(db, item.localId);
        synced++;
      } else if (response.status === 401) {
        item.attempts += 1;
        await putItem(db, item);
        await markAll(db, "auth_blocked", "Autenticação necessária");
        await notifyClients({ type: "AUTH_REQUIRED" });
        break;
      } else if (shouldRetryStatus(response.status)) {
        await bump(db, item, "retrying", `HTTP ${response.status}`, response.headers?.get("Retry-After"));
      } else {
        item.attempts += 1;
        await setState(db, item, "rejected", `HTTP ${response.status}`);
      }
    } catch {
      await bump(db, item, "retrying", "Falha de rede");
    }
  }
  await notifyClients({ type: "TELEMETRY_SYNC_RESULT", synced, counts: await countBy(db) });
  await notifyClients({ type: "TELEMETRY_QUEUE_STATUS", counts: await countBy(db), items: await queueSummaries(db) });
  } finally { syncInProgress = false; }
}

async function queueRequest(request) {
  const payload = await request.json();
  const headers = {};
  request.headers.forEach((value, key) => {
    headers[key] = value;
  });
  await queueTelemetry(payload, headers, request.url);
}

async function queueTelemetry(
  payload,
  headers = {},
  url = `${apiConfig.apiUrl}/telemetria/`,
) {
  const db = await openDb();
  const item = {
    localId: crypto.randomUUID(),
    payload,
    headers,
    url,
    createdAt: new Date().toISOString(),
    state: "pending",
    attempts: 0,
    last_error: null,
    next_attempt_at: 0,
  };
  await putItem(db, item);
  await notifyClients({ type: "TELEMETRY_QUEUED", localId: item.localId });
}

function isTelemetryPost(request) {
  if (request.method !== "POST") return false;

  const url = new URL(request.url);
  const apiUrl = new URL(apiConfig.apiUrl, self.location.origin);
  const apiTelemetryPath = `${apiUrl.pathname.replace(/\/$/, "")}/telemetria/`;
  const isSameApiHost =
    url.origin === apiUrl.origin && url.pathname === apiTelemetryPath;
  const isProxiedApi = url.pathname === "/api/telemetria/";

  return isSameApiHost || isProxiedApi;
}

function isStaticAssetRequest(request) {
  return ["script", "style", "image", "font", "manifest"].includes(
    request.destination,
  );
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
    return (
      cached ||
      jsonResponse(
        { status: "offline", message: "Dados em cache nao disponiveis." },
        503,
      )
    );
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
    if (request.mode === "navigate") {
      return caches.match("/dashboard") || caches.match("/");
    }
    return new Response("", { status: 404 });
  }
}

function buildHeaders(headers) {
  return {
    ...headers,
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}

function queuedResponse(message) {
  return jsonResponse({ status: "queued", message, offline: true }, 202);
}

function jsonResponse(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function shouldRetryStatus(status) {
  return status === 408 || status === 429 || status >= 500;
}

function normalizeItem(item) {
  if (!["pending", "retrying", "rejected", "auth_blocked"].includes(item.state)) item.state = "pending";
  if (!Number.isInteger(item.attempts) || item.attempts < 0) item.attempts = 0;
  if (typeof item.last_error !== "string" && item.last_error !== null) item.last_error = null;
  if (!Number.isFinite(item.next_attempt_at)) item.next_attempt_at = 0;
}

async function bump(db, item, state, error, retryAfter) {
  normalizeItem(item);
  item.attempts += 1;
  item.state = state;
  item.last_error = error;
  const delay = retryDelay(item.attempts, retryAfter);
  item.next_attempt_at = Date.now() + delay;
  await putItem(db, item);
}

function retryDelay(attempts, retryAfter) {
  if (retryAfter) {
    const seconds = Number(retryAfter);
    const dateDelay = Date.parse(retryAfter) - Date.now();
    const requested = Number.isFinite(seconds) ? seconds * 1000 : dateDelay;
    if (Number.isFinite(requested) && requested > 0) return Math.min(requested, 3600000);
  }
  return Math.min(1000 * (2 ** Math.min(Math.max(attempts - 1, 0), 12)), 3600000);
}

async function setState(db, item, state, error = null) {
  normalizeItem(item);
  item.state = state;
  item.last_error = error;
  item.next_attempt_at = 0;
  await putItem(db, item);
}

async function markAll(db, state, error) {
  const items = await readAll(db);
  for (const item of items) {
    if (item.state === "rejected") continue;
    await setState(db, item, state, error);
  }
}

async function countBy(db) {
  const counts = { pending: 0, retrying: 0, rejected: 0, auth_blocked: 0 };
  for (const item of await readAll(db)) {
    normalizeItem(item);
    counts[counts[item.state] === undefined ? "pending" : item.state]++;
  }
  return counts;
}

async function queueSummaries(db) {
  return (await readAll(db)).map((item) => ({
    localId: item.localId,
    state: item.state || "pending",
    last_error: item.last_error || null,
  }));
}

async function reprocessRejected() {
  const db = await openDb();
  for (const item of await readAll(db)) {
    if (item.state === "rejected") await setState(db, item, "pending");
  }
}

async function releaseAuthBlocked() {
  const db = await openDb();
  for (const item of await readAll(db)) {
    if (item.state === "auth_blocked") await setState(db, item, "pending");
  }
  await notifyClients({ type: "AUTH_RECOVERED" });
}

function normalizeApiUrl(value) {
  const trimmed = String(value || "").replace(/\/+$|\/$/, "");
  if (!trimmed) return "/api";
  if (
    trimmed === "/api" ||
    trimmed.endsWith("/api") ||
    trimmed.includes("/api/")
  ) {
    return trimmed;
  }
  return `${trimmed}/api`;
}

function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(TELEMETRY_STORE)) {
        db.createObjectStore(TELEMETRY_STORE, { keyPath: 'localId' });
      }
      const cursorRequest = request.transaction.objectStore(TELEMETRY_STORE).openCursor();
      cursorRequest.onsuccess = () => {
        const cursor = cursorRequest.result;
        if (!cursor) return;
        const item = cursor.value;
        normalizeItem(item);
        cursor.update(item);
        cursor.continue();
      };
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

function getItem(db, key) {
  return tx(db, "readonly", (store) => store.get(key));
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

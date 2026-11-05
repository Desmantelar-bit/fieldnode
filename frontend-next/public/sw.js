const CACHE_NAME = 'fieldnode-runtime-v3';
const STATIC_CACHE = 'fieldnode-static-v3';
const TELEMETRY_SYNC_TAG = 'fieldnode-telemetria-sync';
const DB_NAME = 'fieldnode-offline';
const DB_VERSION = 2;
const TELEMETRY_STORE = "telemetria-pendente";

let apiConfig = {
  apiUrl: "/api",
};

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
    return;
  }

  if (message.type === "GET_TELEMETRY_QUEUE_STATUS") {
    event.waitUntil(sendQueueStatus(event.ports && event.ports[0]));
    return;
  }

  if (message.type === "RESUME_TELEMETRY_AUTH") {
    event.waitUntil(resumeAuthBlocked().then(requestSync));
    return;
  }

  if (message.type === "REPROCESS_REJECTED_TELEMETRY") {
    event.waitUntil(reprocessRejected().then(requestSync));
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
    event.respondWith(fetch(request).catch(() => caches.match("/")));
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
  const payload = await request.clone().json();
  payload.id = payload.id || crypto.randomUUID();
  const requestForNetwork = new Request(request, {
    body: JSON.stringify(payload),
  });
  const requestForQueue = requestForNetwork.clone();

  try {
    const response = await fetch(requestForNetwork);
    if (response.ok) {
      const body = await response
        .clone()
        .json()
        .catch(() => null);
      const ackError = await validateAck(payload, body);
      if (!ackError) return response;
      await queueRequest(requestForQueue, "rejected", ackError);
      return queuedResponse("ACK inválido; leitura mantida para revisão.");
    }
    if (response.status === 401) {
      await queueRequest(requestForQueue, "auth_blocked", "HTTP 401");
      await markAllAuthBlocked();
      await notifyClients({ type: "AUTH_REQUIRED" });
      await sendQueueStatus();
      return queuedResponse(
        "Autenticação necessária; leitura mantida na fila.",
      );
    }
    if (shouldRetryStatus(response.status)) {
      await queueRequest(requestForQueue, "pending", null);
      await requestSync();
      return queuedResponse(
        "Backend indisponivel. Leitura guardada para reenvio.",
      );
    }
    await queueRequest(
      requestForQueue,
      "rejected",
      `HTTP ${response.status}: ${await safeText(response)}`,
    );
    return response;
  } catch {
    await queueRequest(requestForQueue);
    await requestSync();
    return queuedResponse("Sem conexao. Leitura guardada para reenvio.");
  }
}

async function syncTelemetriaData() {
  const db = await openDb();
  const now = Date.now();
  const items = (await readAll(db)).filter(
    (item) =>
      !["rejected", "auth_blocked"].includes(item.state) &&
      (item.next_attempt_at || 0) <= now,
  );
  let synced = 0;

  for (const item of items) {
    const attemptedItem = { ...item, attempts: (item.attempts || 0) + 1 };
    const apiUrl = new URL(apiConfig.apiUrl, self.location.origin);
    let response;
    try {
      response = await fetch(
        item.url || `${apiUrl.toString().replace(/\/$/, "")}/telemetria/`,
        {
          method: "POST",
          headers: buildHeaders(item.headers),
          body: JSON.stringify(item.payload),
        },
      );
    } catch (error) {
      await bumpRetry(
        db,
        attemptedItem,
        error instanceof Error ? error.message : "rede",
      );
      continue;
    }

    if (response.status === 401) {
      await markAllAuthBlocked(db, attemptedItem);
      await notifyClients({ type: "AUTH_REQUIRED" });
      break;
    }

    if (response.ok) {
      const body = await response
        .clone()
        .json()
        .catch(() => null);
      const ackError = await validateAck(item.payload, body);
      if (ackError) {
        await setItemState(db, attemptedItem, "rejected", ackError);
        continue;
      }
      await deleteItem(db, item.localId);
      synced += 1;
      continue;
    }

    if (shouldRetryStatus(response.status)) {
      await bumpRetry(db, attemptedItem, `HTTP ${response.status}`);
      continue;
    }

    await setItemState(
      db,
      attemptedItem,
      "rejected",
      `HTTP ${response.status}: ${await safeText(response)}`,
    );
  }

  await notifyClients({
    type: "TELEMETRY_SYNC_RESULT",
    synced,
    ...(await countBy(db)),
  });
}

async function queueRequest(request, state = "pending", lastError = null) {
  const payload = await request.json();
  const headers = {};
  request.headers.forEach((value, key) => {
    headers[key] = value;
  });
  return queueTelemetry(payload, headers, request.url, state, lastError, 1);
}

async function queueTelemetry(
  payload,
  headers = {},
  url = `${apiConfig.apiUrl}/telemetria/`,
  state = "pending",
  lastError = null,
  attempts = 0,
) {
  const db = await openDb();
  const itemPayload = { ...payload, id: payload.id || crypto.randomUUID() };
  const item = {
    localId: crypto.randomUUID(),
    payload: itemPayload,
    payload_hash: await payloadHash(itemPayload),
    headers,
    url,
    createdAt: new Date().toISOString(),
    state,
    attempts,
    last_error: lastError,
    next_attempt_at: 0,
  };
  await putItem(db, item);
  await notifyClients({ type: "TELEMETRY_QUEUED", localId: item.localId });
  await sendQueueStatus();
  return item;
}

async function validateAck(payload, body) {
  const ack = body && body.ack;
  if (!ack || !["acked", "duplicate"].includes(ack.status)) {
    return "ACK ausente ou status inválido";
  }
  const expectedMessageId = payload.message_id || payload.id;
  const expectedDeviceId =
    payload.device_id ||
    String(payload.maquina_id || "")
      .trim()
      .toUpperCase();
  const expectedSequence =
    payload.sequence_number == null ? 0 : Number(payload.sequence_number);
  const hash = await payloadHash(payload);
  if (ack.message_id !== expectedMessageId)
    return "message_id divergente no ACK";
  if (ack.device_id !== expectedDeviceId) return "device_id divergente no ACK";
  if (ack.sequence_number !== expectedSequence)
    return "sequence_number divergente no ACK";
  if (ack.payload_hash !== hash) return "payload_hash divergente no ACK";
  if (
    !Number.isInteger(ack.last_acked_sequence) ||
    ack.last_acked_sequence < expectedSequence
  ) {
    return "cursor inválido no ACK";
  }
  return null;
}

async function payloadHash(payload) {
  const logicalPayload = { ...payload };
  delete logicalPayload.id;
  const canonical = pythonCanonicalJson(logicalPayload);
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(canonical),
  );
  return Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
}

function pythonCanonicalJson(value) {
  if (value === null || typeof value !== "object") {
    if (typeof value === "string") return pythonJsonString(value);
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(pythonCanonicalJson).join(", ")}]`;
  }
  return `{${Object.keys(value)
    .sort()
    .map(
      (key) => `${pythonJsonString(key)}: ${pythonCanonicalJson(value[key])}`,
    )
    .join(", ")}}`;
}

function pythonJsonString(value) {
  let result = '"';
  for (const character of value) {
    const code = character.codePointAt(0);
    if (character === '"') result += '\\"';
    else if (character === "\\") result += "\\\\";
    else if (character === "\b") result += "\\b";
    else if (character === "\f") result += "\\f";
    else if (character === "\n") result += "\\n";
    else if (character === "\r") result += "\\r";
    else if (character === "\t") result += "\\t";
    else if (code < 0x20 || code > 0x7e) {
      if (code <= 0xffff) result += `\\u${code.toString(16).padStart(4, "0")}`;
      else {
        const adjusted = code - 0x10000;
        const high = 0xd800 + (adjusted >> 10);
        const low = 0xdc00 + (adjusted & 0x3ff);
        result += `\\u${high.toString(16)}\\u${low.toString(16)}`;
      }
    } else result += character;
  }
  return `${result}"`;
}

async function setItemState(db, item, state, lastError) {
  await putItem(db, {
    ...item,
    state,
    last_error: lastError,
    next_attempt_at: state === "retrying" ? item.next_attempt_at : 0,
  });
}

async function bumpRetry(db, item, reason) {
  const attempts = item.attempts || 1;
  const delay = Math.min(60000, 1000 * 2 ** Math.min(attempts - 1, 6));
  await putItem(db, {
    ...item,
    state: "retrying",
    attempts,
    last_error: reason,
    next_attempt_at: Date.now() + delay,
  });
}

async function markAllAuthBlocked(db, attemptedItem) {
  db = db || (await openDb());
  const items = await readAll(db);
  for (const item of items) {
    if (item.state !== "rejected") {
      await putItem(db, {
        ...item,
        attempts:
          item.localId === attemptedItem?.localId
            ? attemptedItem.attempts
            : item.attempts || 0,
        state: "auth_blocked",
        last_error: "HTTP 401",
      });
    }
  }
}

async function resumeAuthBlocked() {
  const db = await openDb();
  const items = await readAll(db);
  for (const item of items) {
    if (item.state === "auth_blocked") {
      await putItem(db, {
        ...item,
        state: "pending",
        last_error: null,
        next_attempt_at: 0,
      });
    }
  }
}

async function reprocessRejected() {
  const db = await openDb();
  const items = await readAll(db);
  for (const item of items) {
    if (item.state === "rejected") {
      await putItem(db, {
        ...item,
        state: "pending",
        attempts: 0,
        last_error: null,
        next_attempt_at: 0,
      });
    }
  }
}

async function countBy(db) {
  db = db || (await openDb());
  const counts = { pending: 0, retrying: 0, rejected: 0, auth_blocked: 0 };
  for (const item of await readAll(db)) {
    if (item.state in counts) counts[item.state] += 1;
  }
  return counts;
}

async function sendQueueStatus(port) {
  const status = { type: "TELEMETRY_QUEUE_STATUS", ...(await countBy()) };
  if (port) port.postMessage(status);
  else await notifyClients(status);
}

async function safeText(response) {
  try {
    return (await response.clone().text()).slice(0, 1000);
  } catch {
    return "resposta sem corpo legível";
  }
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
    return syncTelemetriaData().catch((error) => {
      console.error("[SW] Telemetria sync failed:", error);
    });
  }
  return Promise.resolve();
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
        db.createObjectStore(TELEMETRY_STORE, { keyPath: "localId" });
      } else {
        const store = request.transaction.objectStore(TELEMETRY_STORE);
        const cursorRequest = store.openCursor();
        cursorRequest.onsuccess = () => {
          const cursor = cursorRequest.result;
          if (!cursor) return;
          const item = cursor.value;
          cursor.update({
            ...item,
            state: item.state || "pending",
            attempts: item.attempts || 0,
            last_error: item.last_error || null,
            next_attempt_at: item.next_attempt_at || 0,
          });
          cursor.continue();
        };
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

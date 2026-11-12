const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function createHarness(seed = []) {
  const rows = new Map(seed.map((item) => [item.localId, structuredClone(item)]));
  const messages = [];
  const listeners = {};
  const store = {
    getAll() { return request(() => [...rows.values()].map((value) => structuredClone(value))); },
    put(item) { return request(() => { rows.set(item.localId, structuredClone(item)); return item.localId; }); },
    delete(key) { return request(() => rows.delete(key)); },
    get(key) { return request(() => rows.get(key)); },
    openCursor() {
      const req = {};
      queueMicrotask(() => {
        const values = [...rows.values()];
        let index = 0;
        const next = () => {
          const value = values[index++];
          req.result = value ? { value: structuredClone(value), update: (v) => rows.set(v.localId, structuredClone(v)), continue: next } : null;
          req.onsuccess?.();
        };
        next();
      });
      return req;
    },
  };
  const db = {
    objectStoreNames: { contains: () => true },
    transaction() { return { objectStore: () => store }; },
  };
  const indexedDB = { open() {
    const req = {};
    queueMicrotask(() => { req.result = db; req.onsuccess?.(); });
    return req;
  } };
  const self = {
    location: { origin: 'https://fieldnode.test' },
    clients: { matchAll: async () => [{ postMessage: (message) => messages.push(message) }] },
    registration: {},
    addEventListener: (name, callback) => { listeners[name] = callback; },
    skipWaiting() {},
  };
  const source = fs.readFileSync(require('node:path').join(__dirname, '../public/sw.js'), 'utf8') + '\nglobalThis.__test = { syncTelemetriaData, countBy, reprocessRejected, releaseAuthBlocked };';
  const context = { self, indexedDB, caches: { open: async () => ({ addAll: async () => {} }), keys: async () => [], delete: async () => {} },
    navigator: { onLine: true }, crypto: require('node:crypto').webcrypto, URL, Response, Headers, Date, Math, JSON, Promise,
    setTimeout, clearTimeout, fetch: async () => { throw new Error('fetch mock not set'); }, console };
  context.globalThis = context;
  vm.runInNewContext(source, context);
  return { rows, messages, api: context.__test, setFetch(fn) { context.fetch = fn; } };
}
function request(action) {
  const req = {};
  queueMicrotask(() => { try { req.result = action(); req.onsuccess?.(); } catch (error) { req.error = error; req.onerror?.(); } });
  return req;
}
function item(localId) { return { localId, payload: { id: localId }, headers: {}, url: '/api/telemetria/', createdAt: new Date().toISOString() }; }
function response(status, retryAfter) { return { ok: status >= 200 && status < 300, status, headers: { get: (name) => name === 'Retry-After' ? retryAfter : null } }; }

(async () => {
  {
    const h = createHarness([item('a'), item('b'), item('c')]);
    const statuses = [200, 400, 200]; let calls = 0;
    h.setFetch(async () => response(statuses[calls++]));
    await h.api.syncTelemetriaData();
    assert.equal(calls, 3); assert.equal(h.rows.size, 1); assert.equal(h.rows.get('b').state, 'rejected');
    assert.equal(h.rows.get('b').last_error, 'HTTP 400');
    assert.equal(h.messages.find((m) => m.type === 'TELEMETRY_SYNC_RESULT').synced, 2);
    console.log('PASS fila [200, 400, 200]: dois removidos após ACK, um rejeitado e terceiro processado');
  }
  {
    const h = createHarness([item('a'), item('b')]); let calls = 0;
    h.setFetch(async () => { calls++; return response(401); });
    await h.api.syncTelemetriaData();
    assert.equal(calls, 1); assert.equal(h.rows.size, 2);
    assert.ok([...h.rows.values()].every((row) => row.state === 'auth_blocked'));
    assert.ok(h.messages.some((m) => m.type === 'AUTH_REQUIRED'));
    await h.api.releaseAuthBlocked();
    assert.ok([...h.rows.values()].every((row) => row.state === 'pending'));
    console.log('PASS 401 bloqueia fila, preserva itens e recuperação libera reenvio');
  }
  {
    const h = createHarness([item('a')]);
    h.setFetch(async () => response(503)); await h.api.syncTelemetriaData();
    const deferred = h.rows.get('a');
    assert.equal(deferred.state, 'retrying'); assert.equal(deferred.attempts, 1);
    assert.ok(deferred.next_attempt_at > Date.now());
    let calls = 0; h.setFetch(async () => { calls++; return response(200); });
    await h.api.syncTelemetriaData(); assert.equal(calls, 0);
    deferred.next_attempt_at = 0; h.rows.set('a', deferred);
    await h.api.syncTelemetriaData(); assert.equal(calls, 1); assert.equal(h.rows.size, 0);
    console.log('PASS 503 reagenda com backoff e só reenvia quando elegível');
  }
  {
    const h = createHarness([item('a')]); h.setFetch(async () => response(429, '120'));
    await h.api.syncTelemetriaData();
    assert.ok(h.rows.get('a').next_attempt_at >= Date.now() + 119000);
    console.log('PASS 429 respeita Retry-After');
  }
  {
    const h = createHarness([item('a')]); h.setFetch(async () => { throw new Error('offline'); });
    await h.api.syncTelemetriaData();
    assert.equal(h.rows.get('a').state, 'retrying'); assert.equal(h.rows.get('a').last_error, 'Falha de rede');
    await h.api.reprocessRejected();
    console.log('PASS falha de rede é isolada e registrada por item');
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });



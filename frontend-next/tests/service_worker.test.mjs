import assert from "node:assert/strict";
import { createHash, webcrypto } from "node:crypto";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const source = await readFile(new URL("../public/sw.js", import.meta.url), "utf8");

function canonicalJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(", ")}]`;
  return `{${Object.keys(value).sort().map((key) =>
    `${JSON.stringify(key)}: ${canonicalJson(value[key])}`,
  ).join(", ")}}`;
}

function payloadHash(payload) {
  const logicalPayload = { ...payload };
  delete logicalPayload.id;
  return createHash("sha256").update(canonicalJson(logicalPayload)).digest("hex");
}

test("hash lógico coincide com o vetor Python do backend e edge", () => {
  const payload = {
    id: "row-ignored",
    device_id: "EDGE-ACK-01",
    message_id: "logical-message-1",
    sequence_number: 7,
    maquina_id: "EDGE-ACK-01",
    temperatura: 86,
    vibracao: 0.35,
    rpm: 1800,
    timestamp: "2026-11-05T12:00:00Z",
    time_source: "unsynced",
    boot_id: "12345678-1234-5678-1234-567812345678",
    uptime_ms: 7000,
  };

  assert.equal(
    payloadHash(payload),
    "62d356c473139e1d59d1d36bd0b6ddb01e91e3b621aeb0fbc582b302161e36e1",
  );
});

function makePayload(id) {
  return {
    id,
    maquina_id: "EDGE-ACK-01",
    temperatura: 86,
    vibracao: 2,
    rpm: 1800,
    timestamp: "2026-11-05T12:00:00Z",
  };
}

function makeItem(id, overrides = {}) {
  const payload = makePayload(id);
  return {
    localId: `local-${id}`,
    payload,
    payload_hash: payloadHash(payload),
    headers: {},
    url: "/api/telemetria/",
    state: "pending",
    attempts: 0,
    last_error: null,
    next_attempt_at: 0,
    ...overrides,
  };
}

function ackResponse(payload, overrides = {}) {
  const ack = {
    status: "acked",
    message_id: payload.id,
    device_id: payload.maquina_id,
    sequence_number: payload.sequence_number ?? 0,
    payload_hash: payloadHash(payload),
    last_acked_sequence: payload.sequence_number ?? 0,
    ...overrides,
  };
  return new Response(JSON.stringify({ ack }), { status: 201 });
}

function createHarness(items, responses) {
  const rows = new Map(items.map((item) => [item.localId, structuredClone(item)]));
  const handlers = new Map();
  const clientMessages = [];

  function request(result, action = () => {}) {
    const output = { result, onsuccess: null, onerror: null };
    queueMicrotask(() => {
      action();
      output.onsuccess?.({ target: output });
    });
    return output;
  }

  const store = {
    getAll: () => request([...rows.values()].map((item) => structuredClone(item))),
    put: (item) => request(item.localId, () => rows.set(item.localId, structuredClone(item))),
    delete: (key) => request(undefined, () => rows.delete(key)),
    openCursor: () => request(null),
  };
  const database = { transaction: () => ({ objectStore: () => store }) };
  const indexedDB = { open: () => request(database) };
  const self = {
    location: { origin: "https://fieldnode.test" },
    registration: {},
    clients: {
      matchAll: async () => [{ postMessage: (message) => clientMessages.push(message) }],
    },
    addEventListener: (type, handler) => handlers.set(type, handler),
    skipWaiting: () => Promise.resolve(),
  };
  const context = {
    self,
    indexedDB,
    crypto: webcrypto,
    TextEncoder,
    URL,
    Request,
    Response,
    Headers,
    Date,
    console,
    navigator: { onLine: true },
    caches: { open: async () => ({ addAll: async () => {} }) },
    fetch: async (...args) => {
      const next = responses.shift();
      if (next instanceof Error) throw next;
      if (!next) throw new Error("No mock response configured");
      return next;
    },
  };
  vm.runInNewContext(source, context, { filename: "sw.js" });

  return {
    rows,
    clientMessages,
    async sync() {
      let promise;
      handlers.get("sync")({
        tag: "fieldnode-telemetria-sync",
        waitUntil: (value) => { promise = value; },
      });
      await promise;
    },
    async fetchTelemetry(request) {
      let responsePromise;
      handlers.get("fetch")({
        request,
        respondWith: (value) => { responsePromise = value; },
      });
      return responsePromise;
    },
    async sendMessage(type) {
      let promise;
      handlers.get("message")({
        data: { type },
        ports: [],
        waitUntil: (value) => { promise = value; },
      });
      await promise;
    },
    fetchCount: () => responses.length,
  };
}

test("POST online só retorna sucesso com ACK coerente", async () => {
  const payload = makePayload("online-ack-1");
  const harness = createHarness([], [ackResponse(payload)]);
  const response = await harness.fetchTelemetry(new Request(
    "https://fieldnode.test/api/telemetria/",
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) },
  ));

  assert.equal(response.status, 201);
  assert.equal(harness.rows.size, 0);
});

test("POST online com ACK inconsistente mantém item rejeitado", async () => {
  const payload = makePayload("online-ack-invalid-1");
  const harness = createHarness(
    [],
    [ackResponse(payload, { payload_hash: "0".repeat(64) })],
  );
  const response = await harness.fetchTelemetry(new Request(
    "https://fieldnode.test/api/telemetria/",
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) },
  ));

  assert.equal(response.status, 202);
  assert.equal(harness.rows.size, 1);
  assert.equal([...harness.rows.values()][0].state, "rejected");
});

test("ACK válido com hash, identidade e sequência remove o item", async () => {
  const item = makeItem("valid-1");
  const harness = createHarness([item], [ackResponse(item.payload)]);

  await harness.sync();

  assert.equal(harness.rows.size, 0);
  assert.equal(harness.clientMessages.at(-1).synced, 1);
});

test("fila antiga com hash que inclui id continua sincronizando", async () => {
  const item = makeItem("legacy-hash-1");
  item.payload_hash = createHash("sha256")
    .update(canonicalJson(item.payload))
    .digest("hex");
  const harness = createHarness([item], [ackResponse(item.payload)]);

  await harness.sync();

  assert.equal(harness.rows.size, 0);
});

test("hash divergente rejeita o ACK e mantém o item", async () => {
  const item = makeItem("hash-1");
  const harness = createHarness(
    [item],
    [ackResponse(item.payload, { payload_hash: "0".repeat(64) })],
  );

  await harness.sync();

  assert.equal(harness.rows.get(item.localId).state, "rejected");
  assert.match(harness.rows.get(item.localId).last_error, /payload_hash/);
});

test("sequência divergente rejeita o ACK e mantém o item", async () => {
  const payload = { ...makePayload("sequence-1"), sequence_number: 4 };
  const item = makeItem("sequence-1", {
    payload,
    payload_hash: payloadHash(payload),
  });
  const harness = createHarness(
    [item],
    [ackResponse(payload, { sequence_number: 5, last_acked_sequence: 5 })],
  );

  await harness.sync();

  assert.equal(harness.rows.get(item.localId).state, "rejected");
  assert.match(harness.rows.get(item.localId).last_error, /sequence_number/);
});

test("resposta 2xx sem ACK JSON válido não remove o item", async () => {
  const item = makeItem("invalid-ack-1");
  const harness = createHarness([item], [new Response("not-json", { status: 200 })]);

  await harness.sync();

  assert.equal(harness.rows.get(item.localId).state, "rejected");
  assert.match(harness.rows.get(item.localId).last_error, /ACK/);
});

test("falha de rede mantém e reagenda o item com backoff", async () => {
  const item = makeItem("network-1");
  const harness = createHarness([item], [new Error("offline")]);

  await harness.sync();

  const saved = harness.rows.get(item.localId);
  assert.equal(saved.state, "retrying");
  assert.equal(saved.attempts, 1);
  assert.ok(saved.next_attempt_at > Date.now());
});

test("400 rejeita um item e não bloqueia os itens seguintes", async () => {
  const first = makeItem("batch-1");
  const invalid = makeItem("batch-2");
  const last = makeItem("batch-3");
  const harness = createHarness(
    [first, invalid, last],
    [
      ackResponse(first.payload),
      new Response("invalid payload", { status: 400 }),
      ackResponse(last.payload),
    ],
  );

  await harness.sync();

  assert.equal(harness.rows.size, 1);
  assert.equal(harness.rows.get(invalid.localId).state, "rejected");
  assert.equal(harness.clientMessages.at(-1).synced, 2);
});

test("401 bloqueia a fila inteira até autenticação", async () => {
  const first = makeItem("auth-1");
  const second = makeItem("auth-2");
  const harness = createHarness(
    [first, second],
    [new Response("unauthorized", { status: 401 })],
  );

  await harness.sync();

  assert.deepEqual(
    [...harness.rows.values()].map((item) => item.state),
    ["auth_blocked", "auth_blocked"],
  );
  assert.ok(harness.clientMessages.some((message) => message.type === "AUTH_REQUIRED"));
});

test("503 mantém o item em retrying com backoff exponencial", async () => {
  const item = makeItem("server-error-1");
  const harness = createHarness([item], [new Response("unavailable", { status: 503 })]);

  await harness.sync();

  const saved = harness.rows.get(item.localId);
  assert.equal(saved.state, "retrying");
  assert.equal(saved.attempts, 1);
  assert.ok(saved.next_attempt_at > Date.now());
});

test("reprocessar rejeitadas reinicia estado e tenta novamente", async () => {
  const item = makeItem("reprocess-1", {
    state: "rejected",
    last_error: "HTTP 400",
  });
  const harness = createHarness([item], [ackResponse(item.payload)]);

  await harness.sendMessage("REPROCESS_REJECTED_TELEMETRY");

  assert.equal(harness.rows.size, 0);
  assert.equal(harness.clientMessages.at(-1).synced, 1);
});
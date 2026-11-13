import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import test from 'node:test';

const require = createRequire(import.meta.url);
const ts = require('typescript');
const source = await readFile(new URL('../src/services/apiRead.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;
const module = { exports: {} };
vm.runInNewContext(compiled, {
  exports: module.exports,
  fetch: (...args) => globalThis.fetch(...args),
  AbortController,
  setTimeout,
  clearTimeout,
  Response,
  DOMException,
  URLSearchParams,
  console,
  process: { env: { NODE_ENV: 'test' } },
});
const { getValidated, ApiReadError } = module.exports;

test('validated reader returns parsed payload and classifies contract and HTTP failures', async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({ count: 2 }), { status: 200 });
  assert.deepEqual(await getValidated('events/', { safeParse: (value) => ({ success: true, data: value }) }), { count: 2 });

  globalThis.fetch = async () => new Response('{"wrong":true}', { status: 200 });
  await assert.rejects(() => getValidated('events/', { safeParse: () => ({ success: false, error: { issues: [] } }) }),
    (error) => error instanceof ApiReadError && error.kind === 'invalido');

  globalThis.fetch = async () => new Response('{}', { status: 401 });
  await assert.rejects(() => getValidated('events/', { safeParse: () => ({ success: true, data: {} }) }),
    (error) => error instanceof ApiReadError && error.kind === 'auth');
});

test('validated reader passes cancellation to fetch and classifies connection failures', async () => {
  const controller = new AbortController();
  let observedSignal;
  globalThis.fetch = (_url, options) => new Promise((_resolve, reject) => {
    observedSignal = options.signal;
    options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
  });
  const pending = getValidated('events/', { safeParse: (value) => ({ success: true, data: value }) }, controller.signal);
  controller.abort();
  await assert.rejects(pending, (error) => error.name === 'AbortError');
  assert.equal(observedSignal.aborted, true);

  globalThis.fetch = async () => { throw new TypeError('network'); };
  await assert.rejects(() => getValidated('events/', { safeParse: (value) => ({ success: true, data: value }) }),
    (error) => error instanceof ApiReadError && error.kind === 'network');
});

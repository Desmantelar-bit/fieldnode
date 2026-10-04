const assert = require('node:assert/strict');
const { chromium } = require('playwright');

const BASE_URL = process.env.FIELDNODE_TEST_BASE_URL || 'http://127.0.0.1:3001';
const EMPTY_RESPONSE = [];

const pages = [
  {
    path: '/colheitadeiras',
    apiPath: '/leituras/ultimas/',
    loading: 'Carregando leituras de telemetria...',
    empty: 'Nenhuma leitura encontrada.',
    error: 'Não foi possível carregar as máquinas.',
    log: '[FieldNode] colheitadeiras:',
  },
  {
    path: '/operarios',
    apiPath: '/operario/',
    loading: 'Carregando operarios...',
    empty: 'Nenhum operario cadastrado.',
    error: 'Não foi possível carregar os operários.',
    log: '[FieldNode] operarios:',
  },
  {
    path: '/dashboard',
    apiPath: '/colheitadeira/',
    loadingSelector: '[aria-label="Carregando dados da frota"]',
    empty: 'Nenhuma colheitadeira cadastrada ainda.',
    error: 'Dashboard indisponível',
    log: '[FieldNode] dashboard:',
  },
  {
    path: '/detalhes?id=7',
    apiPath: '/telemetria/',
    loading: 'Carregando historico da maquina...',
    empty: 'Nenhuma leitura encontrada.',
    error: 'Não foi possível carregar o histórico.',
    log: '[FieldNode] detalhes:',
  },
];

function deferred() {
  let resolve;
  const promise = new Promise((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

async function mockApi(page, { failFirstPath, holdPath, readings } = {}) {
  const attempts = new Map();
  const requestSeen = deferred();
  const responseGate = deferred();

  await page.route('**/api/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname;
    const attempt = (attempts.get(pathname) || 0) + 1;
    attempts.set(pathname, attempt);

    if (holdPath && pathname.includes(holdPath)) {
      requestSeen.resolve();
      await responseGate.promise;
    }

    if (failFirstPath && pathname.includes(failFirstPath) && attempt === 1) {
      await route.abort();
      return;
    }

    const body = readings && pathname.includes('/leituras/ultimas/')
      ? readings
      : EMPTY_RESPONSE;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(body),
    });
  });

  return { attempts, requestSeen, responseGate };
}

async function verifyLoadingAndEmpty(browser, testCase) {
  const page = await browser.newPage();
  const { requestSeen, responseGate } = await mockApi(page, { holdPath: testCase.apiPath });

  await page.goto(`${BASE_URL}${testCase.path}`, { waitUntil: 'domcontentloaded' });
  await requestSeen.promise;

  const loading = testCase.loadingSelector
    ? page.locator(testCase.loadingSelector)
    : page.getByText(testCase.loading, { exact: false });
  try {
    await loading.waitFor({ state: 'visible', timeout: 4000 });
  } catch (error) {
    const body = (await page.locator('body').innerText()).replace(/\s+/g, ' ');
    responseGate.resolve();
    throw new Error(`loading não apareceu em ${testCase.path}; DOM: ${body}`, { cause: error });
  }
  responseGate.resolve();
  await page.getByText(testCase.empty, { exact: false }).waitFor({ timeout: 10000 });

  const body = await page.locator('body').innerText();
  if (testCase.path === '/dashboard') {
    assert.doesNotMatch(body, /1820|78°C|2\.1/);
    assert.doesNotMatch(body, /RPM médio|Temperatura média|Vibração média/);
  }

  await page.close();
}

async function verifyErrorAndRetry(browser, testCase) {
  const page = await browser.newPage();
  const consoleErrors = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  const { attempts } = await mockApi(page, { failFirstPath: testCase.apiPath });

  await page.goto(`${BASE_URL}${testCase.path}`, { waitUntil: 'domcontentloaded' });
  await page.getByRole('heading', { name: testCase.error, exact: false }).waitFor({ timeout: 15000 });
  assert.equal(await page.getByRole('button', { name: 'Tentar novamente' }).count(), 1);
  assert.doesNotMatch(await page.locator('body').innerText(), /Failed to fetch|HTTP 50\d/);
  assert.ok(consoleErrors.some((message) => message.includes(testCase.log)), 'erro técnico deve ser registrado no console');

  await page.getByRole('button', { name: 'Tentar novamente' }).click();
  await page.getByText(testCase.empty, { exact: false }).waitFor({ timeout: 15000 });
  assert.ok([...attempts.values()].some((count) => count >= 2), 'retry deve repetir a chamada da API');
  await page.close();
}

async function verifyDashboardMetrics(browser) {
  const page = await browser.newPage();
  const readings = [
    { maquina_id: 'M-01', temperatura: 70, vibracao: 0.4, rpm: 1600, timestamp: '2026-10-04T12:00:00Z' },
    { maquina_id: 'M-02', temperatura: 80, vibracao: 0.6, rpm: 2000, timestamp: '2026-10-04T12:01:00Z' },
  ];
  await mockApi(page, { readings });

  await page.goto(`${BASE_URL}/dashboard`, { waitUntil: 'domcontentloaded' });
  await page.getByRole('group', { name: 'RPM médio' }).waitFor({ timeout: 15000 });

  assert.match(await page.getByRole('group', { name: 'RPM médio' }).innerText(), /1800/);
  assert.match(await page.getByRole('group', { name: 'Temperatura média' }).innerText(), /75\.0 °C/);
  assert.match(await page.getByRole('group', { name: 'Vibração média' }).innerText(), /0\.50 g/);
  await page.close();
}

async function verifyDashboardTelemetryRetry(browser) {
  const page = await browser.newPage();
  await mockApi(page, { failFirstPath: '/leituras/ultimas/' });

  await page.goto(`${BASE_URL}/dashboard`, { waitUntil: 'domcontentloaded' });
  await page.getByRole('heading', { name: 'Indicadores indisponíveis' }).waitFor({ timeout: 15000 });
  await page.getByRole('button', { name: 'Tentar novamente' }).click();
  await page.getByText('Nenhuma leitura de telemetria encontrada.', { exact: false }).waitFor({ timeout: 15000 });
  await page.close();
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const testCase of pages) {
      await verifyLoadingAndEmpty(browser, testCase);
      console.log(`PASS loading/vazio ${testCase.path}`);
      await verifyErrorAndRetry(browser, testCase);
      console.log(`PASS erro/retry ${testCase.path}`);
    }
    await verifyDashboardMetrics(browser);
    console.log('PASS métricas derivadas de telemetria real');
    await verifyDashboardTelemetryRetry(browser);
    console.log('PASS retry de erro parcial no dashboard');
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { setTimeout as delay } from 'node:timers/promises';
import test from 'node:test';
import { chromium } from 'playwright';

const root = new URL('..', import.meta.url).pathname;
const port = 3217;
const baseUrl = `http://127.0.0.1:${port}`;
const machineId = 'INT-MOT-01';
const timestamp = '2026-11-12T12:00:00Z';
const browserPath = process.env.PLAYWRIGHT_CHROMIUM_PATH || '/usr/bin/chromium';

const user = {
  id: 1,
  username: 'ui-test',
  email: 'ui-test@example.invalid',
  first_name: 'UI',
  last_name: 'Test',
};

const telemetryReading = {
  id: '11111111-1111-4111-8111-111111111111',
  maquina_id: machineId,
  temperatura: 88,
  vibracao: 2.2,
  vibracao_unit: 'indice_0_10',
  rpm: 1500,
  timestamp,
  status_risco: { rotuloRisco: 'NORMAL' },
};

const canReading = {
  id: '22222222-2222-4222-8222-222222222222',
  maquina_id: machineId,
  timestamp,
  recebido_em: timestamp,
  simulado: true,
  rpm: 1500,
  carga_pct: 55,
  horimetro_h: 1200,
  oleo_pressao_kpa: 90,
  oleo_temp_c: 135,
  oleo_nivel_pct: 70,
  liquido_temp_c: 108,
  liquido_nivel_pct: 85,
  rail_pressao_kpa: 150000,
  combustivel_temp_c: 45,
  consumo_lh: 30,
  turbo_pressao_kpa: 210,
  escape_temp_c: 500,
  bateria_v: 13.8,
};

const prescriptions = [
  {
    subsistema: 'combustivel_alta_pressao', status: 'NORMAL', evidencia_nivel: 'BAIXA',
    sinais_usados: [], sinais_indisponiveis: [], horas_ate_limite: null, limite_referencia: null,
    motivo_estimativa: 'Sem tendência consistente.', diagnostico: 'Sinais na faixa de referência.',
    acao: 'Manter monitoramento.', prazo: 'Monitoramento', dtcs_relacionados: [],
  },
  {
    subsistema: 'admissao', status: 'ATENCAO', evidencia_nivel: 'MEDIA',
    sinais_usados: [{ sinal: 'turbo_pressao_kpa', valor: 80, unidade: 'kPa', concorda: true }],
    sinais_indisponiveis: [], horas_ate_limite: null, limite_referencia: null,
    motivo_estimativa: 'Menos de 12 observações.', diagnostico: 'Inspecionar a admissão.',
    acao: 'Verificar dutos.', prazo: 'Monitoramento', dtcs_relacionados: [],
  },
  {
    subsistema: 'lubrificacao', status: 'CRITICO', evidencia_nivel: 'MEDIA',
    sinais_usados: [{ sinal: 'oleo_pressao_kpa', valor: 90, unidade: 'kPa', concorda: true }],
    sinais_indisponiveis: [], horas_ate_limite: null,
    limite_referencia: { sinal: 'oleo_pressao_kpa', valor: 120, unidade: 'kPa', direcao: 'abaixo', origem: 'Referência ilustrativa do protótipo.' },
    motivo_estimativa: 'Menos de 12 observações.', diagnostico: '<img id="unsafe-markup" src=x onerror="window.__xss=1">',
    acao: 'Verificar nível e pressão.', prazo: 'Imediata',
    dtcs_relacionados: [{ spn: 100, fmi: 1, descricao_referencia: 'Referência contextual.' }],
  },
  {
    subsistema: 'arrefecimento', status: 'ATENCAO', evidencia_nivel: 'BAIXA',
    sinais_usados: [{ sinal: 'liquido_temp_c', valor: 108, unidade: '°C', concorda: true }],
    sinais_indisponiveis: [], horas_ate_limite: null,
    limite_referencia: { sinal: 'liquido_temp_c', valor: 112, unidade: '°C', direcao: 'acima', origem: 'Referência ilustrativa do protótipo.' },
    motivo_estimativa: 'Menos de 12 observações.', diagnostico: 'Confirmar temperatura.',
    acao: 'Inspecionar o sistema.', prazo: 'Monitoramento', dtcs_relacionados: [],
  },
];

const canResponse = {
  ultima_leitura: canReading,
  serie: [
    { ...canReading, id: '33333333-3333-4333-8333-333333333333', timestamp: '2026-11-12T11:59:55Z', recebido_em: '2026-11-12T11:59:56Z' },
    canReading,
  ],
  dtcs_ativos: [{
    spn: 100, fmi: 1, ocorrencias: 2, ativo: true, primeira_vez: '2026-11-12T11:30:00Z',
    ultima_vez: timestamp, subsistema: 'lubrificacao', descricao_referencia: 'Referência contextual.', simulado: true,
  }],
  prescricoes: prescriptions,
  qualidade: {
    recebidas: 5, aceitas: 4, descartadas: 1,
    motivos: { oleo_pressao_kpa_fora_faixa_fisica: 1 },
    campos_ausentes: { oleo_temp_c: 1 },
    sinais_congelados: { rpm: 1 },
  },
  simulado: true,
  origem_dados: 'SIMULADO',
};

const emptyCanResponse = {
  ultima_leitura: null,
  serie: [],
  dtcs_ativos: [],
  prescricoes: ['arrefecimento', 'lubrificacao', 'combustivel_alta_pressao', 'admissao'].map((subsistema) => ({
    subsistema, status: null, evidencia_nivel: 'BAIXA', sinais_usados: [],
    sinais_indisponiveis: ['nenhuma leitura válida disponível'], horas_ate_limite: null,
    limite_referencia: null, motivo_estimativa: 'Estimativa indisponível: não há leituras válidas.',
    diagnostico: 'Prescrição indisponível: ausência de dados não significa condição normal.',
    acao: 'Verificar conectividade e qualidade da telemetria.', prazo: 'Monitoramento', dtcs_relacionados: [],
  })),
  qualidade: { recebidas: 0, aceitas: 0, descartadas: 0, motivos: {}, campos_ausentes: {}, sinais_congelados: {} },
  simulado: true,
  origem_dados: 'SIMULADO',
};

async function waitForServer(server) {
  let lastError = '';
  for (let attempt = 0; attempt < 60; attempt += 1) {
    if (server.exitCode !== null) throw new Error(`Next.js encerrou: ${lastError}`);
    try {
      const response = await fetch(baseUrl);
      if (response.ok) return;
    } catch (error) {
      lastError = String(error);
    }
    await delay(500);
  }
  throw new Error(`Next.js não iniciou: ${lastError}`);
}

test('módulo Motor CAN: navegação, decisão, DTC, gráficos, qualidade e polling', { timeout: 45000 }, async () => {
  assert.ok(existsSync(browserPath), `Chromium não encontrado em ${browserPath}`);
  const standalone = `${root}/.next/standalone`;
  const standaloneStatic = `${standalone}/.next/static`;
  rmSync(standaloneStatic, { recursive: true, force: true });
  mkdirSync(`${standalone}/.next`, { recursive: true });
  cpSync(`${root}/.next/static`, standaloneStatic, { recursive: true });
  if (existsSync(`${root}/public`)) {
    cpSync(`${root}/public`, `${standalone}/public`, { recursive: true });
  }
  const server = spawn(process.execPath, [
    '.next/standalone/server.js',
  ], {
    cwd: root,
    env: {
      ...process.env,
      NEXT_TELEMETRY_DISABLED: '1',
      HOSTNAME: '127.0.0.1',
      PORT: String(port),
    },
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  let stderr = '';
  server.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
  let browser;
  let context;

  try {
    await waitForServer(server);
    browser = await chromium.launch({
      executablePath: browserPath,
      headless: true,
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    });
    context = await browser.newContext({
      viewport: { width: 1440, height: 1100 },
      serviceWorkers: 'block',
    });
    const page = await context.newPage();
    const canRequests = [];
    const observed = [];
    page.on('pageerror', (error) => observed.push(`pageerror: ${error.message}`));
    page.on('response', (response) => observed.push(`${response.status()} ${response.url()}`));
    await page.addInitScript((authUser) => {
      localStorage.setItem('fn-auth-user', JSON.stringify(authUser));
    }, user);
    await page.route('**/api/auth/me/**', (route) => route.fulfill({
      status: 200, contentType: 'application/json', body: JSON.stringify(user),
    }));
    await page.route('**/api/telemetria/**', (route) => route.fulfill({
      status: 200, contentType: 'application/json', body: JSON.stringify([telemetryReading]),
    }));
    await page.route('**/api/can/motor/**', async (route) => {
      canRequests.push(route.request().url());
      const requestMachine = new URL(route.request().url()).searchParams.get('maquina_id');
      if (requestMachine === 'INT-MOT-EMPTY') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(emptyCanResponse) });
        return;
      }
      if (requestMachine === machineId && canRequests.filter((url) => new URL(url).searchParams.get('maquina_id') === machineId).length === 2) {
        await delay(6000);
        await route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ detail: 'indisponível' }) });
        return;
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(canResponse) });
    });

    await page.goto(`${baseUrl}/detalhes?id=${encodeURIComponent(machineId)}`);
    const motorLink = page.locator(`a[href="/motor/${machineId}"]`);
    try {
      await motorLink.waitFor({ state: 'visible', timeout: 10000 });
    } catch {
      throw new Error(`Link Motor não apareceu. URL=${page.url()}\nBody=${(await page.locator('body').innerText()).slice(0, 3000)}\nRequests=${observed.join('\n')}`);
    }
    await motorLink.click();
    try {
      await page.getByText('DADOS SIMULADOS', { exact: true }).waitFor({ state: 'visible', timeout: 10000 });
    } catch {
      throw new Error(`Página Motor sem banner. URL=${page.url()}\nBody=${(await page.locator('body').innerText()).slice(0, 3000)}\nRequests=${observed.join('\n')}`);
    }
    assert.equal(new URL(page.url()).pathname, `/motor/${machineId}`);
    assert.ok(canRequests[0]?.includes(`maquina_id=${machineId}`), 'o id da máquina deve ser enviado à API CAN');

    const cardTitles = await page.locator('section[aria-labelledby="prescriptions-title"] article h3').allTextContents();
    assert.deepEqual(cardTitles, ['Lubrificação', 'Admissão', 'Arrefecimento', 'Combustível de alta pressão']);
    assert.equal(await page.locator('section[aria-labelledby="dtc-title"] .metric-card').count(), 1);
    assert.match(await page.locator('section[aria-labelledby="dtc-title"]').innerText(), /SPN 100 · FMI 1/);
    assert.match(await page.locator('section[aria-labelledby="dtc-title"]').innerText(), /Primeira ocorrência/);
    assert.match(await page.locator('section[aria-labelledby="dtc-title"]').innerText(), /Última ocorrência/);
    assert.ok(await page.getByText('Leituras recebidas', { exact: true }).count());
    assert.ok(await page.getByText('Sinais congelados', { exact: true }).count());
    assert.ok(await page.getByText('Horário', { exact: true }).count());
    assert.ok(await page.getByText('Limite usado:', { exact: false }).count());
    assert.equal(await page.locator('#unsafe-markup').count(), 0, 'conteúdo da API deve ser renderizado como texto, nunca como HTML');
    assert.equal(await page.evaluate(() => window.__xss ?? 0), 0);
    assert.match(await page.locator('section[aria-labelledby="prescriptions-title"]').innerText(), /<img id="unsafe-markup"/);

      await page.getByText('Atualização indisponível; mantendo a última resposta recebida.', { exact: false }).waitFor({ state: 'visible', timeout: 15000 });
    assert.equal(await page.locator('section[aria-labelledby="prescriptions-title"] article h3').first().innerText(), 'Lubrificação');
    assert.equal(canRequests.length, 2, 'a atualização periódica deve aguardar a chamada anterior');

    await page.goto(`${baseUrl}/login`);
    await delay(5500);
    assert.equal(canRequests.length, 2, 'o polling deve parar quando a página do módulo é abandonada');

    await page.goto(`${baseUrl}/motor/INT-MOT-EMPTY`);
    await page.getByText('Ainda não há leituras CAN válidas.', { exact: true }).waitFor({ state: 'visible', timeout: 10000 });
    assert.match(await page.locator('section[aria-labelledby="dtc-title"]').innerText(), /Nenhum DTC ativo recebido/);
    assert.match(await page.locator('section[aria-labelledby="prescriptions-title"]').innerText(), /ausência de dados não significa condição normal/);
    assert.match(await page.locator('section[aria-labelledby="motor-readings-title"]').innerText(), /Nenhuma leitura válida/);
    await page.goto(`${baseUrl}/login`);
    await delay(5500);
    assert.equal(canRequests.length, 3, 'o polling também deve parar na página sem dados ao abandoná-la');
  } catch (error) {
    if (stderr) throw new Error(`${String(error)}\nNext.js stderr:\n${stderr}`);
    throw error;
  } finally {
    await context?.close();
    await browser?.close();
    server.kill('SIGTERM');
  }
});

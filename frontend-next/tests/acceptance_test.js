/* eslint-disable @typescript-eslint/no-require-imports */
/**
 * Bateria de aceitação 9.4 (Mapa) + 9.5 (Relatórios)
 * Porta detectada automaticamente: tenta 3001, fallback 3000.
 */
const { chromium } = require('playwright');
const http = require('http');

const MOCK_POSITIONS = [
  { id: 1, maquina_id: 'COLH-01', lat: -15.793889, lng: -47.882778, status: 'operando', telemetria: { temperatura: 72, rpm: 1850, timestamp: new Date().toISOString() } },
  { id: 2, maquina_id: 'COLH-02', lat: -15.80,    lng: -47.90,    status: 'parada',   telemetria: { temperatura: 85, rpm: 1300, timestamp: new Date().toISOString() } },
];

async function detectPort() {
  for (const port of [3001, 3000]) {
    const ok = await new Promise((resolve) => {
      const req = http.get(`http://localhost:${port}/dashboard`, { timeout: 4000 }, (res) => { res.resume(); resolve(true); });
      req.on('error', () => resolve(false));
      req.on('timeout', () => { req.destroy(); resolve(false); });
    });
    if (ok) return port;
  }
  throw new Error('Nenhuma porta respondeu');
}

function pass(msg) { console.log('  ✅ ' + msg); }
function fail(msg) { console.log('  ❌ ' + msg); }
function section(msg) { console.log('\n── ' + msg + ' ──'); }

(async () => {
  let BASE;
  try {
    const port = await detectPort();
    BASE = `http://localhost:${port}`;
  } catch (e) {
    console.error('FATAL:', e.message);
    process.exit(1);
  }

  console.log(`\n🔍 Testando em ${BASE}\n`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  const consoleErrors = [];
  const networkErrors = [];
  page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', (err) => consoleErrors.push(err.message));
  page.on('response', (res) => { if (res.status() >= 400 && res.url().includes('/api/')) networkErrors.push(`${res.status()} ${res.url()}`); });

  // ─────────────────────────────────────────────
  // 9.4 — MAPA
  // ─────────────────────────────────────────────
  section('9.4 MAPA — carregamento');

  // Mock GPS com 2 máquinas válidas
  await page.route('**/api/maquinas/posicao/**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_POSITIONS) })
  );

  await page.goto(`${BASE}/mapa`, { waitUntil: 'domcontentloaded', timeout: 30000 });

  // Aguarda Leaflet ou mensagem de estado
  const leafletLoaded = await page.waitForSelector('.leaflet-container, [class*="EmptyState"], [class*="ErrorState"]', { timeout: 20000 }).then(() => true).catch(() => false);
  leafletLoaded ? pass('Página /mapa carregou sem crash') : fail('Página /mapa não carregou componente esperado');

  const hasLeaflet = await page.locator('.leaflet-container').count() > 0;
  hasLeaflet ? pass('leaflet-container presente no DOM') : fail('leaflet-container ausente');

  // Geometria — sem scroll horizontal
  const scrollX = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  scrollX <= 5 ? pass(`Sem scroll horizontal (overflow: ${scrollX}px)`) : fail(`Scroll horizontal detectado: ${scrollX}px`);

  // Fundo escuro (não branco)
  const bgColor = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  !bgColor.includes('255, 255, 255') ? pass(`Fundo escuro: ${bgColor}`) : fail(`Fundo branco detectado: ${bgColor}`);

  section('9.4 MAPA — painel de status');
  const panel = page.locator('aside[aria-label*="status" i], aside[aria-label*="frota" i]').first();
  const panelVisible = await panel.isVisible().catch(() => false);
  panelVisible ? pass('Painel de status visível') : fail('Painel de status não encontrado');

  if (panelVisible) {
    const panelText = await panel.innerText();
    panelText.includes('9') ? pass('Valor 9 (Normal) presente no painel') : fail(`Valor 9 não encontrado no painel: "${panelText}"`);
    panelText.includes('2') ? pass('Valor 2 (Atenção) presente no painel') : fail(`Valor 2 não encontrado no painel`);
    panelText.includes('1') ? pass('Valor 1 (Crítico) presente no painel') : fail(`Valor 1 não encontrado no painel`);

    // Painel não ultrapassa viewport
    const box = await panel.boundingBox();
    if (box) {
      box.x + box.width <= 1920 ? pass('Painel dentro da viewport (horizontal)') : fail('Painel ultrapassa viewport');
      box.y + box.height <= 1080 ? pass('Painel dentro da viewport (vertical)') : fail('Painel ultrapassa viewport verticalmente');
    }
  }

  section('9.4 MAPA — marcadores (pílulas)');
  if (hasLeaflet) {
    // Aguarda markers renderizarem
    await page.waitForTimeout(3000);
    const markerCount = await page.locator('.leaflet-machine-pill-icon, .leaflet-marker-icon').count();
    markerCount > 0 ? pass(`${markerCount} marcador(es) no mapa`) : fail('Nenhum marcador encontrado');

    const pillCount = await page.locator('.leaflet-machine-pill-icon').count();
    pillCount > 0 ? pass(`${pillCount} pílula(s) divIcon encontrada(s)`) : fail('Nenhuma pílula divIcon encontrada');

    // Verifica conteúdo da pílula
    const pillHtml = await page.locator('.leaflet-machine-pill-icon').first().innerHTML().catch(() => '');
    pillHtml.includes('COLH') ? pass('ID da máquina visível na pílula') : fail(`ID não encontrado na pílula: "${pillHtml.slice(0, 100)}"`);
    (pillHtml.includes('Operando') || pillHtml.includes('Atenção') || pillHtml.includes('Offline'))
      ? pass('Status visível na pílula')
      : fail('Status não encontrado na pílula');
    pillHtml.includes('🚜') ? pass('Ícone 🚜 presente') : fail('Ícone 🚜 ausente');

    // Clica no primeiro marker e verifica popup
    const firstMarker = page.locator('.leaflet-machine-pill-icon').first();
    await firstMarker.click({ force: true }).catch(() => {});
    await page.waitForTimeout(800);
    const popupVisible = await page.locator('.leaflet-popup').isVisible().catch(() => false);
    popupVisible ? pass('Popup abre ao clicar no marcador') : fail('Popup não abriu');
  }

  section('9.4 MAPA — console');
  const mapErrors = consoleErrors.filter(e =>
    /window is not defined|hydrat|leaflet|import/i.test(e)
  );
  mapErrors.length === 0 ? pass('Console limpo (sem erros Leaflet/hidratação)') : fail(`Erros no console: ${mapErrors.join(' | ')}`);

  // Screenshot mapa
  await page.screenshot({ path: 'tests/screenshot_mapa.png', fullPage: false }).catch(() => {});
  pass('Screenshot salvo em tests/screenshot_mapa.png');

  // ─────────────────────────────────────────────
  // 9.5 — RELATÓRIOS
  // ─────────────────────────────────────────────
  consoleErrors.length = 0;
  networkErrors.length = 0;

  section('9.5 RELATÓRIOS — carregamento');
  await page.goto(`${BASE}/relatorios`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);

  const relBg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  !relBg.includes('255, 255, 255') ? pass(`Fundo escuro: ${relBg}`) : fail('Fundo branco no /relatorios');

  const h1 = await page.locator('h1').first().innerText().catch(() => '');
  h1.length > 0 ? pass(`Título presente: "${h1}"`) : fail('Título h1 não encontrado');

  // Mega-card claro
  const lightCard = page.locator('.bg-slate-50, .bg-white').first();
  const cardVisible = await lightCard.isVisible().catch(() => false);
  cardVisible ? pass('Mega-card claro (bg-slate-50/white) presente') : fail('Mega-card claro não encontrado');

  section('9.5 RELATÓRIOS — filtros');
  const machineSelect = page.locator('select').first();
  const selectVisible = await machineSelect.isVisible().catch(() => false);
  selectVisible ? pass('Select de máquina visível') : fail('Select de máquina não encontrado');

  if (selectVisible) {
    const options = await machineSelect.locator('option').count();
    options > 0 ? pass(`${options} opção(ões) no select de máquina`) : fail('Select vazio');
  }

  const periodSelect = page.locator('select').nth(1);
  const periodVisible = await periodSelect.isVisible().catch(() => false);
  periodVisible ? pass('Select de período visível') : fail('Select de período não encontrado');

  section('9.5 RELATÓRIOS — botão Atualizar dados');
  const updateBtn = page.locator('button', { hasText: /atualizar dados/i }).first();
  const updateBtnVisible = await updateBtn.isVisible().catch(() => false);
  updateBtnVisible ? pass('Botão "Atualizar dados" visível') : fail('Botão "Atualizar dados" não encontrado');

  if (updateBtnVisible && selectVisible) {
    const requests = [];
    page.on('request', (req) => { if (req.url().includes('/relatorio')) requests.push(req.url()); });
    await updateBtn.click();
    await page.waitForTimeout(3000);
    requests.length > 0 ? pass(`Requisição disparada: ${requests[0]}`) : fail('Nenhuma requisição para /relatorio após clicar Atualizar');
  }

  section('9.5 RELATÓRIOS — exportação XLSX');
  const exportBtn = page.locator('button', { hasText: /exportar/i }).first();
  const exportBtnVisible = await exportBtn.isVisible().catch(() => false);
  exportBtnVisible ? pass('Botão Exportar visível') : fail('Botão Exportar não encontrado');

  if (exportBtnVisible) {
    const exportDisabled = await exportBtn.evaluate((el) => el.disabled);
    !exportDisabled ? pass('Botão Exportar habilitado') : fail('Botão Exportar está disabled');

    if (!exportDisabled) {
      const exportRequests = [];
      page.on('request', (req) => { if (req.url().includes('exportar')) exportRequests.push(req.url()); });
      // Intercepta navegação para não sair da página
      await page.route('**/relatorio/exportar/**', (route) =>
        route.fulfill({ status: 200, contentType: 'text/csv', body: 'maquina;data\nCOLH-01;2026-01-01' })
      );
      await exportBtn.click();
      await page.waitForTimeout(1500);
      exportRequests.length > 0
        ? pass(`Requisição de exportação disparada: ${exportRequests[0]}`)
        : fail('Nenhuma requisição para /relatorio/exportar após clicar Exportar');
    }
  }

  section('9.5 RELATÓRIOS — console');
  const relErrors = consoleErrors.filter(e => !/favicon|manifest/i.test(e));
  relErrors.length === 0 ? pass('Console limpo em /relatorios') : fail(`Erros: ${relErrors.slice(0, 3).join(' | ')}`);

  await page.screenshot({ path: 'tests/screenshot_relatorios.png', fullPage: false }).catch(() => {});
  pass('Screenshot salvo em tests/screenshot_relatorios.png');

  // ─────────────────────────────────────────────
  // INTEGRAÇÃO — navegação completa
  // ─────────────────────────────────────────────
  section('INTEGRAÇÃO — Dashboard → Mapa → Relatórios → Dashboard');
  const navErrors = [];

  for (const [label, url] of [['Dashboard', '/dashboard'], ['Mapa', '/mapa'], ['Relatórios', '/relatorios'], ['Dashboard', '/dashboard']]) {
    try {
      const res = await page.goto(`${BASE}${url}`, { waitUntil: 'domcontentloaded', timeout: 20000 });
      res?.status() === 200 ? pass(`${label} (${url}) → 200`) : fail(`${label} → ${res?.status()}`);
      const sx = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      sx <= 5 ? pass(`  sem scroll horizontal em ${url}`) : fail(`  scroll horizontal ${sx}px em ${url}`);
    } catch (e) {
      fail(`${label} falhou: ${e.message}`);
      navErrors.push(label);
    }
  }

  await browser.close();
  console.log('\n── FIM DA BATERIA ──\n');
})();

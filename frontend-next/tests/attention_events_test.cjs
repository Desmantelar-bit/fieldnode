const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.addInitScript(() => localStorage.setItem('fn-auth-user', JSON.stringify({ id: 1, username: 'evidence', first_name: 'Teste', last_name: '', email: '' })));
  await page.route('**/api/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname;
    if (pathname.endsWith('/auth/me/')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ id: 1, username: 'evidence', first_name: 'Teste', last_name: '', email: '' }) });
    } else if (pathname.endsWith('/events/')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ count: 2, results: [
        { id: '11111111-1111-4111-8111-111111111111', machine_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', machine_external_code: 'COLH-120', tipo: 'TEMP_ALTA', severidade: 'CRITICO', status: 'ABERTO', trust_score_herdado: 0.2, priority_score: '1.0000', evidence_quality: 'insuficiente', needs_verification: true, criado_em: '2026-11-12T12:00:00Z' },
        { id: '22222222-2222-4222-8222-222222222222', machine_id: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb', machine_external_code: 'COLH-02', tipo: 'TEMP_ALTA', severidade: 'ATENCAO', status: 'ABERTO', trust_score_herdado: 0.95, priority_score: '0.5000', evidence_quality: 'boa', needs_verification: false, criado_em: '2026-11-12T11:00:00Z' },
      ] }) });
    } else {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
    }
  });
  try {
    await page.goto('http://127.0.0.1:3001/dashboard', { waitUntil: 'domcontentloaded' });
    const panel = page.getByRole('region', { name: 'Atenção operacional Eventos prioritários' });
    await page.getByRole('heading', { name: 'Eventos prioritários' }).waitFor({ timeout: 15000 });
    const rows = panel.locator('li');
    assert.equal(await rows.count(), 2);
    assert.match(await rows.nth(0).innerText(), /CRITICO[\s\S]*COLH-120[\s\S]*Verificar leitura[\s\S]*1\.00/);
    assert.match(await rows.nth(1).innerText(), /ATENCAO[\s\S]*COLH-02[\s\S]*0\.50/);
    assert.doesNotMatch(await rows.nth(1).innerText(), /Verificar leitura|Evidência suspeita/);
    await page.screenshot({ path: path.resolve(__dirname, '../../docs/evidence/s1/S1-T3-attention-events.png'), fullPage: false });
    console.log('PASS eventos ordenados por priority_score; evento grave com evidência insuficiente exibe selo sem rebaixar severidade');
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });

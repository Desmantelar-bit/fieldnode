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
      return;
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', results: [], count: 0 }) });
  });
  try {
    await page.goto('http://127.0.0.1:3001/dashboard', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);
    await page.evaluate(() => window.dispatchEvent(new CustomEvent('fieldnode-queue-status', { detail: {
      counts: { pending: 2, retrying: 1, rejected: 1, auth_blocked: 1 },
      items: [{ localId: 'rejected-12345678', state: 'rejected', last_error: 'HTTP 422' }],
    } })));
    await page.getByText('2 pendentes · 1 retentativas').waitFor({ timeout: 10000 });
    await page.getByText('· 1 rejeitadas').waitFor();
    await page.getByText('· 1 aguardam login').waitFor();
    await page.getByText('Autenticação necessária.').waitFor();
    await page.getByText('Ver erros').click();
    await page.getByText(/HTTP 422/).waitFor();
    await page.screenshot({ path: path.resolve(__dirname, '../../docs/evidence/s1/S1-T4-queue-indicator.png'), fullPage: false });
    console.log('PASS indicador apresenta contagens, rejeição, erro e login; captura salva');
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });


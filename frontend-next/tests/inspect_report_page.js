const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', (msg) => {
    console.log('PAGE_CONSOLE', msg.type(), msg.text());
  });

  page.on('pageerror', (err) => {
    console.error('PAGE_ERROR', err.message);
  });

  page.on('request', (request) => {
    if (request.url().includes('/api/colheitadeira')) {
      console.log('REQUEST', request.method(), request.url(), JSON.stringify(request.headers()));
    }
  });

  page.on('response', async (response) => {
    if (response.url().includes('/api/colheitadeira')) {
      console.log('RESPONSE', response.status(), response.url(), response.headers()['content-type']);
      try {
        const body = await response.text();
        console.log('RESPONSE_BODY', body.slice(0, 500).replace(/\n/g, ' '));
      } catch (e) {
        console.log('RESPONSE_BODY_ERROR', e.message);
      }
    }
  });

  await page.goto('http://127.0.0.1:3005/relatorios', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(5000);

  const machineSelect = page.locator('div:has-text("Maquina") select').first();
  const selectCount = await machineSelect.count();
  console.log('SELECT_COUNT', selectCount);
  if (selectCount > 0) {
    const options = await machineSelect.locator('option').allInnerTexts();
    console.log('SELECT_OPTIONS', options);
    console.log('SELECT_VALUE', await machineSelect.evaluate((el) => el.value));
  }

  const button = page.locator('button', { hasText: 'Gerar relatorio' }).first();
  console.log('BUTTON_COUNT', await button.count());
  if ((await button.count()) > 0) {
    console.log('BUTTON_DISABLED', await button.evaluate((el) => el.disabled));
    console.log('BUTTON_TEXT', await button.innerText());
  }

  await browser.close();
})();

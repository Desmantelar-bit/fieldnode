/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const http = require('node:http');

const POSITIONS = [0, 1, 2, 3].map((index) => ({
  id: index + 1,
  maquina_id: `COLH-0${index + 1}`,
  modelo: 'TC5000',
  lat: -15.793889 + index * 0.0003,
  lng: -47.882778 + index * 0.0003,
  status: index === 0 ? 'operando' : 'parada',
  telemetria: { temperatura: 72, rpm: 1800, timestamp: new Date().toISOString() },
}));

async function baseUrl() {
  for (const port of [3001, 3000]) {
    const isUp = await new Promise((resolve) => {
      const request = http.get(`http://localhost:${port}/mapa`, { timeout: 3000 }, (response) => {
        response.resume();
        resolve(true);
      });
      request.on('error', () => resolve(false));
      request.on('timeout', () => { request.destroy(); resolve(false); });
    });
    if (isUp) return `http://localhost:${port}`;
  }
  throw new Error('Nenhum servidor Next.js respondeu nas portas 3001 ou 3000.');
}

(async () => {
  const base = await baseUrl();
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    serviceWorkers: 'block',
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));

  try {
    await page.route('**/api/health/**', (route) => route.fulfill({ status: 503, body: '{}' }));
    await page.route('**/api/maquinas/posicao/**', (route) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(POSITIONS),
    }));
    await page.goto(`${base}/mapa`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForSelector('.leaflet-machine-cluster', { timeout: 15000 });
    assert.equal(await page.locator('#map-client-debug').count(), 0, 'Badge de debug ainda está visível.');
    assert.equal(await page.locator('.map-machine-cluster__count').first().innerText(), '4');

    const cluster = page.locator('.leaflet-machine-cluster').first();
    await cluster.focus();
    await cluster.press('Enter');
    const machineOption = page.getByRole('button', { name: /Abrir COLH-01/ });
    await machineOption.waitFor({ state: 'visible', timeout: 5000 });
    await machineOption.click();
    await page.waitForFunction(() => {
      const popup = document.querySelector('.leaflet-popup-content');
      return Boolean(popup && popup.textContent.includes('COLH-01'));
    }, null, { timeout: 5000 });

    await page.reload({ waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForSelector('.leaflet-machine-cluster', { timeout: 15000 });
    for (let index = 0; index < 8; index += 1) {
      await page.locator('.leaflet-control-zoom-in').evaluate((element) => {
        element.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      });
      await page.waitForTimeout(100);
    }
    await page.waitForFunction(() => document.querySelectorAll('.leaflet-machine-cluster').length === 0, null, { timeout: 7000 });
    assert.equal(await page.locator('.leaflet-machine-marker').count(), 4);

    const rail = await page.locator('.app-nav--rail').evaluate((element) => {
      const style = getComputedStyle(element);
      return { radius: style.borderRadius, divider: style.borderRightWidth };
    });
    assert.equal(rail.radius, '0px');
    assert.ok(Number.parseFloat(rail.divider) >= 0.5, `Divisor do rail invisível: ${rail.divider}.`);

    const theme = await page.evaluate(() => document.documentElement.classList.contains('light') ? 'light' : 'dark');
    await page.getByRole('button', { name: theme === 'light' ? 'Ativar modo escuro' : 'Ativar modo claro' }).click();
    const lightText = await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--text-3').trim());
    assert.equal(lightText.toLowerCase(), '#4b5563');

    await page.setViewportSize({ width: 390, height: 844 });
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(overflow <= 5, `Overflow horizontal de ${overflow}px em mobile.`);
    assert.equal(await page.locator('#map-client-debug').count(), 0);

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`${base}/operarios`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const operatorCard = page.getByRole('button', { name: /Ver detalhes de/ }).first();
    const hasOperators = await operatorCard.isVisible().catch(() => false);
    if (hasOperators) {
      await operatorCard.click({ timeout: 5000 });
      const dialog = page.getByRole('dialog');
      await dialog.waitFor({ state: 'visible', timeout: 5000 });
      const style = await dialog.evaluate((element) => ({
        width: element.getBoundingClientRect().width,
        padding: getComputedStyle(element).padding,
      }));
      assert.ok(style.width <= 520 && style.width >= 440, `Largura do modal inesperada: ${style.width}px.`);
      assert.equal(style.padding, '24px');
      await page.setViewportSize({ width: 390, height: 844 });
      assert.ok((await dialog.evaluate((element) => element.getBoundingClientRect().width)) <= 366);
    } else {
      console.log('SKIP — modal real: serviço de operários indisponível neste ambiente.');
    }
    assert.equal(errors.length, 0, errors.join('; '));

    console.log('PASS — clusters, seleção por teclado, marcador individual, rail, tema claro e overflow mobile.');
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

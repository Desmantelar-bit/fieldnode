/* eslint-disable @typescript-eslint/no-require-imports */
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');

const outputDir = path.resolve(__dirname, '../../docs/evidence/s3/captures');
const baseUrl = process.env.FIELDNODE_TEST_BASE_URL || 'http://127.0.0.1:3000';
const machine = {
  id: 3,
  maquina_id: 'CH-03',
  modelo: 'Colheitadeira demonstrativa',
  latitude: -23.5,
  longitude: -46.6,
  status: 'operando',
  telemetria: { temperatura: 96, rpm: 1800, timestamp: '2026-11-13T17:00:00Z' },
};

async function tap(page, locator) {
  const rect = await locator.boundingBox();
  await page.mouse.click(rect.x + rect.width / 2, rect.y + rect.height / 2);
}

(async () => {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('console', (message) => { if (message.type() === 'error') pageErrors.push(message.text()); });

  try {
    await page.route('**/api/auth/me/', (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ id: 1, username: 'test', email: '', first_name: '', last_name: '' }) }));
    await page.route('**/api/maquinas/posicao/**', (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([machine]) }));

    await page.goto(`${baseUrl}/mapa`, { waitUntil: 'domcontentloaded' });
    await page.locator('.leaflet-marker-icon').first().waitFor({ timeout: 30000 });
    await page.screenshot({ path: path.join(outputDir, 's3-t7-map-mobile.png'), style: 'nextjs-portal { display: none !important; }' });

    const marker = page.locator('.leaflet-marker-icon').first();
    await tap(page, marker.locator('.map-machine-marker__icon'));
    const sheet = page.locator('.map-mobile-sheet');
    await sheet.waitFor();
    if (await page.locator('.leaflet-popup').count()) throw new Error('O popup Leaflet duplicado apareceu junto da bottom sheet mobile.');
    await page.getByText('96 °C').waitFor();
    await page.getByText('1800 rpm').waitFor();
    await page.keyboard.press('Shift+Tab');
    if (!(await page.evaluate(() => document.activeElement?.getAttribute('href')?.startsWith('/detalhes?id=')))) throw new Error('A contenção de foco da bottom sheet não alcança sua última ação.');
    await page.keyboard.press('Tab');
    if (!(await page.evaluate(() => document.activeElement?.getAttribute('aria-label') === 'Fechar detalhes da máquina'))) throw new Error('A navegação por teclado não retorna ao início da bottom sheet.');
    const sheetMetrics = await sheet.evaluate((element) => {
      const rect = element.getBoundingClientRect();
      const map = document.querySelector('.leaflet-container').getBoundingClientRect();
      const overlap = Math.max(0, Math.min(map.bottom, rect.bottom) - Math.max(map.top, rect.top));
      return { height: rect.height, top: rect.top, viewport: window.innerHeight, mapHeight: map.height, overlap };
    });
    if (sheetMetrics.height > sheetMetrics.viewport * 0.45 + 1) throw new Error(`Sheet excedeu 45% da viewport: ${JSON.stringify(sheetMetrics)}`);
    if (sheetMetrics.mapHeight - sheetMetrics.overlap < sheetMetrics.mapHeight * 0.55 - 1) throw new Error(`Mapa ficou visível em menos de 55%: ${JSON.stringify(sheetMetrics)}`);
    await page.screenshot({ path: path.join(outputDir, 's3-t7-bottom-sheet.png'), style: 'nextjs-portal { display: none !important; }' });
    await page.getByRole('button', { name: 'Fechar detalhes da máquina' }).click();
    await sheet.waitFor({ state: 'detached' });
    if (!(await page.evaluate(() => document.activeElement?.classList.contains('leaflet-marker-icon')))) throw new Error('Foco não retornou ao marcador após fechar a sheet.');

    await page.locator('.leaflet-marker-icon').first().focus();
    await page.keyboard.press('Enter');
    await page.keyboard.press('Escape');
    await page.locator('.map-mobile-sheet').waitFor({ state: 'detached' });

    await tap(page, page.locator('.leaflet-marker-icon').first().locator('.map-machine-marker__icon'));
    const touchPoint = await page.locator('.map-mobile-sheet').evaluate((el) => {
      const r = el.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + 15 };
    });
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: touchPoint.x, y: touchPoint.y, id: 1 }] });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: touchPoint.x, y: touchPoint.y + 110, id: 1 }] });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await cdp.detach();
    await page.locator('.map-mobile-sheet').waitFor({ state: 'detached' });

    await page.getByRole('button', { name: /Filtros/ }).click();
    const drawer = page.getByRole('dialog', { name: 'Buscar máquina' });
    await drawer.waitFor();
    await page.waitForTimeout(220);
    await page.keyboard.press('Shift+Tab');
    if (!(await page.evaluate(() => document.activeElement?.tagName === 'INPUT'))) throw new Error('A contenção de foco da gaveta não retornou ao último controle.');
    await page.keyboard.press('Tab');
    if (!(await page.evaluate(() => document.activeElement?.getAttribute('aria-label') === 'Fechar gaveta de filtros'))) throw new Error('A navegação por teclado não retornou ao início da gaveta.');
    await page.screenshot({ path: path.join(outputDir, 's3-t7-filter-drawer.png'), style: 'nextjs-portal { display: none !important; }' });
    await drawer.getByPlaceholder('ID, modelo ou status').fill('CH-03');
    await page.getByText('1 resultado(s)').waitFor();
    await page.getByRole('button', { name: 'Fechar gaveta de filtros' }).click();
    await drawer.waitFor({ state: 'detached' });
    if (!(await page.evaluate(() => document.activeElement?.getAttribute('aria-haspopup') === 'dialog'))) throw new Error('Foco não retornou ao controle de filtros.');
    if (!new URL(page.url()).searchParams.get('q')?.includes('CH-03')) throw new Error('Busca não foi persistida no parâmetro q.');
    await page.screenshot({ path: path.join(outputDir, 's3-t7-filter-preserved.png'), style: 'nextjs-portal { display: none !important; }' });
    await page.getByRole('button', { name: /Filtros/ }).click();
    await page.getByRole('dialog', { name: 'Buscar máquina' }).getByPlaceholder('ID, modelo ou status').waitFor();
    if (await page.getByPlaceholder('ID, modelo ou status').inputValue() !== 'CH-03') throw new Error('Busca foi perdida ao fechar e reabrir a gaveta.');
    await page.keyboard.press('Escape');
    await page.locator('[role="dialog"][aria-labelledby="map-filter-title"]').waitFor({ state: 'detached' });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.locator('.leaflet-marker-icon').first().waitFor();
    if (!(await page.getByRole('button', { name: /Filtros/ }).innerText()).includes('1')) throw new Error('Busca não foi restaurada após recarregar.');
    await page.getByRole('button', { name: /Filtros/ }).click();
    await page.getByPlaceholder('ID, modelo ou status').waitFor();
    if (await page.getByPlaceholder('ID, modelo ou status').inputValue() !== 'CH-03') throw new Error('Parâmetro q não restaurou o valor do campo após recarregar.');
    await page.getByRole('button', { name: 'Limpar busca' }).click();
    if (new URL(page.url()).searchParams.has('q')) throw new Error('Limpar busca não removeu q da URL.');
    await page.keyboard.press('Escape');

    await page.getByRole('button', { name: /Por trás do FieldNode|Conheça quem faz o FieldNode/ }).click();
    const teamPanel = page.getByRole('dialog', { name: 'Quem está por trás do FieldNode' });
    await teamPanel.waitFor();
    await page.waitForTimeout(220);
    for (const name of ['Vinícius Morales', 'Ana Furlaneto', "Giovana D'Angelo", 'Paola Soares Machado']) await teamPanel.getByRole('heading', { name }).waitFor();
    await teamPanel.locator('img').evaluateAll((images) => Promise.all(images.map((image) => image.decode())));
    if (await teamPanel.locator('img').evaluateAll((images) => images.some((image) => image.naturalWidth === 0))) throw new Error('Uma fotografia não carregou no painel mobile.');
    for (const [name, url] of [['Vinícius Morales', 'https://github.com/ViniciusMorales'], ['Ana Furlaneto', 'https://github.com/acfurlaneto'], ['Paola Soares Machado', 'https://github.com/Paola5858']]) {
      const githubLink = teamPanel.getByRole('link', { name: new RegExp(`GitHub de ${name}`) });
      if (await githubLink.getAttribute('href') !== url) throw new Error(`URL GitHub incorreta para ${name}.`);
      if (await githubLink.getAttribute('target') !== '_blank' || await githubLink.getAttribute('rel') !== 'noopener noreferrer') throw new Error(`Abertura externa insegura ou inconsistente para ${name}.`);
    }
    await page.keyboard.press('Shift+Tab');
    if (!(await page.evaluate(() => document.activeElement?.getAttribute('href') === 'https://github.com/Paola5858'))) throw new Error('A contenção de foco do painel da equipe não funcionou.');
    await teamPanel.evaluate((element) => { element.scrollTop = 0; });
    await page.waitForTimeout(100);
    if (await teamPanel.getByRole('link', { name: /GitHub de Giovana/ }).count()) throw new Error('Giovana recebeu um GitHub não informado.');
    await page.screenshot({ path: path.join(outputDir, 's3-t8-team-mobile.png'), style: 'nextjs-portal { display: none !important; }' });
    await teamPanel.evaluate((element) => { element.scrollTop = element.scrollHeight; });
    await page.waitForTimeout(100);
    await page.screenshot({ path: path.join(outputDir, 's3-t8-team-mobile-bottom.png'), style: 'nextjs-portal { display: none !important; }' });
    await page.keyboard.press('Escape');
    await teamPanel.waitFor({ state: 'detached' });
    if (!(await page.getByRole('button', { name: 'Conheça quem faz o FieldNode' }).evaluate((element) => element === document.activeElement))) throw new Error('Foco mobile não retornou ao acionador do painel da equipe.');

    await page.setViewportSize({ width: 1440, height: 960 });
    await page.getByRole('button', { name: /Por trás do FieldNode/ }).click();
    const desktopTeamPanel = page.getByRole('dialog', { name: 'Quem está por trás do FieldNode' });
    await desktopTeamPanel.waitFor();
    await page.waitForTimeout(220);
    await desktopTeamPanel.locator('img').evaluateAll((images) => Promise.all(images.map((image) => image.decode())));
    await page.screenshot({ path: path.join(outputDir, 's3-t8-team-desktop.png'), style: 'nextjs-portal { display: none !important; }' });
    await page.keyboard.press('Escape');
    if (!(await page.getByRole('button', { name: /Por trás do FieldNode/ }).evaluate((element) => element === document.activeElement))) throw new Error('Foco desktop não retornou ao acionador do painel da equipe.');

    if (pageErrors.length) throw new Error(`Erros no navegador: ${pageErrors.join('\n')}`);
    console.log(`Playwright S3-T7/T8 aprovado. Evidências: ${outputDir}`);
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });

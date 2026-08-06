const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  const logs = [];
  const fs = require('fs');

  page.on('console', msg => {
    try { logs.push({ type: 'console', text: msg.text(), location: msg.location() }); } catch(e) { logs.push({ type: 'console', text: String(msg) }); }
  });
  page.on('pageerror', err => logs.push({ type: 'pageerror', text: err.message, stack: err.stack }));
  page.on('request', r => logs.push({ type: 'request', url: r.url(), method: r.method() }));
  page.on('response', async res => {
    try { logs.push({ type: 'response', url: res.url(), status: res.status() }); } catch(e) { logs.push({ type: 'response', url: res.url() }); }
  });

  // Helper to pretty print a header
  const printHeader = (title) => console.log('\n==== ' + title + ' ====');

  try {
    // Scenario 1: empty positions
    await page.route('**/api/maquinas/posicao/**', route => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) }));
    await page.goto('http://127.0.0.1:3000/mapa', { waitUntil: 'domcontentloaded' });
    // Wait explicitly for the MapContainer to appear (up to 15s)
    try {
      await page.waitForSelector('.leaflet-container', { timeout: 15000 });
    } catch (e) {
      // Continue to collect logs even if selector not found
    }
    await page.reload({ waitUntil: 'domcontentloaded' });
    try { await page.waitForSelector('.leaflet-container', { timeout: 10000 }); } catch (e) {}
    await page.goto('http://127.0.0.1:3000/dashboard', { waitUntil: 'domcontentloaded' });
    await page.goto('http://127.0.0.1:3000/mapa', { waitUntil: 'domcontentloaded' });
    try { await page.waitForSelector('.leaflet-container', { timeout: 10000 }); } catch (e) {}

    // collect number of leaflet containers in DOM
    const containersAfter = await page.evaluate(() => document.querySelectorAll('.leaflet-container').length);
    console.log('LEAFLET_CONTAINERS_AFTER_EMPTY=' + containersAfter);
    try { await page.screenshot({ path: 'c:/temp/map_empty.png', fullPage: true }); } catch(e) {}
    try { fs.writeFileSync('c:/temp/play_logs_empty.json', JSON.stringify(logs, null, 2)); } catch (e) {}
    try { const html = await page.content(); fs.writeFileSync('c:/temp/map_empty.html', html); } catch(e) {}

    printHeader('TEST_EMPTY_POSITIONS');
    console.log(JSON.stringify(logs, null, 2));

    // Scenario 2: with a machine position
    logs.length = 0;
    await page.unroute('**/api/maquinas/posicao/**');
    await page.route('**/api/maquinas/posicao/**', route => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([{ id: 'COLH-01', latitude: -23.5, longitude: -46.6 }]) }));
    await page.reload({ waitUntil: 'domcontentloaded' });
    try { await page.waitForSelector('.leaflet-container', { timeout: 15000 }); } catch (e) {}

    const containersAfterWithData = await page.evaluate(() => document.querySelectorAll('.leaflet-container').length);
    try { await page.screenshot({ path: 'c:/temp/map_with_data.png', fullPage: true }); } catch(e) {}
    try { fs.writeFileSync('c:/temp/play_logs_with_data.json', JSON.stringify(logs, null, 2)); } catch (e) {}
    try { const html2 = await page.content(); fs.writeFileSync('c:/temp/map_with_data.html', html2); } catch(e) {}
    printHeader('TEST_WITH_POSITIONS');
    console.log(JSON.stringify(logs, null, 2));
    console.log('LEAFLET_CONTAINERS_AFTER_WITH_DATA=' + containersAfterWithData);

  } catch (err) {
    console.error('TEST_ERROR', err);
  } finally {
    await browser.close();
  }
})();

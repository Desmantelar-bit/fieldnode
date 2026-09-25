import { chromium } from 'playwright';
import fs from 'fs';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('requestfailed', request => console.log('REQ FAILED:', request.url()));
  page.on('response', async response => {
    const url = response.url();
    if (url.includes('decisions') || url.includes('prescricoes')) {
      console.log('RESPONSE:', response.status(), url);
    }
  });

  await page.goto('http://127.0.0.1:3000');
  await page.evaluate(() => {
    localStorage.setItem('fieldnode_auth_token', '8710584852c4b1adf92f6f2cb3c7cc7a025121c4');
    document.cookie = 'fieldnode_token=8710584852c4b1adf92f6f2cb3c7cc7a025121c4; path=/';
  });

  await page.goto('http://127.0.0.1:3000/colheitadeiras');
  await page.waitForTimeout(6000);
  await page.screenshot({ path: '../evidence_debug_dashboard.png' });

  await page.waitForSelector('button:has-text("Ver")', { timeout: 20000 });
  await page.locator('button:has-text("Ver")').first().click({ force: true });

  await page.waitForSelector('button:has-text("Aprovar")', { timeout: 20000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: '../evidence_1_pendente.png' });
  console.log('Screenshot 1 (PENDENTE) OK');

  await page.locator('button:has-text("Aprovar")').click({ force: true });
  console.log('Clicou em Aprovar, aguardando resposta...');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '../evidence_2_after_approve.png' });
  console.log('Screenshot 2 (pos-aprovar) OK');

  const hasMarcar = await page.locator('button:has-text("Marcar")').count();
  console.log('hasMarcar:', hasMarcar);

  if (hasMarcar > 0) {
    await page.evaluate(() => { window.confirm = () => true; });
    await page.locator('button:has-text("Marcar")').click({ force: true });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '../evidence_3_executada.png' });
    console.log('Screenshot 3 (EXECUTADA) OK');
  } else {
    const pageText = await page.locator('body').innerText();
    fs.writeFileSync('../debug_modal_text.txt', pageText);
    console.log('Botao Marcar nao encontrado. Texto salvo em debug_modal_text.txt');
  }

  await browser.close();
  console.log('DONE');
})().catch(err => { console.error('ERRO:', err.message); process.exit(1); });

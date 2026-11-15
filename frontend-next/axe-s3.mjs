import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';

const base = process.env.FIELDNODE_FRONTEND_URL || 'http://127.0.0.1:3000';
const token = process.env.FIELDNODE_AUTH_TOKEN;
if (!token) throw new Error('Defina FIELDNODE_AUTH_TOKEN para executar a auditoria autenticada.');
const routes = ['/dashboard', '/colheitadeiras', '/decisoes', '/mapa', '/operarios', '/relatorios'];
const browser = await chromium.launch({ headless: true });
const results = [];
try {
  for (const theme of ['light', 'dark']) for (const route of routes) {
    const context = await browser.newContext();
    await context.addInitScript(({ authToken, selectedTheme }) => { localStorage.setItem('fn-auth-token', authToken); localStorage.setItem('fn-theme', selectedTheme); }, { authToken: token, selectedTheme: theme });
    const page = await context.newPage();
    await page.goto(`${base}${route}`, { waitUntil: 'networkidle' });
    await page.evaluate((selectedTheme) => { document.documentElement.classList.remove('light', 'dark'); document.documentElement.classList.add(selectedTheme); }, theme);
    const axe = await new AxeBuilder({ page }).analyze();
    results.push({ route, theme, violations: axe.violations });
    await context.close();
  }
} finally { await browser.close(); }
await fs.mkdir('../docs/evidence/s3', { recursive: true });
await fs.writeFile('../docs/evidence/s3/s3-t9-axe.json', JSON.stringify({ generated_at: new Date().toISOString(), results }, null, 2));
console.log(JSON.stringify(results.map(({ route, theme, violations }) => ({ route, theme, serious: violations.filter((v) => ['serious', 'critical'].includes(v.impact)).length, total: violations.length }))));

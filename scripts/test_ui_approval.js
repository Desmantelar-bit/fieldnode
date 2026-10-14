const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../frontend-next/node_modules/playwright'));
const fs = require('fs');

async function runUiApproval({ trialNum, outcomeText, recordVideo = false, machineId = 'COLH-01' }) {
  const videoDir = path.resolve(__dirname, '../artifacts/s10/videos');
  if (!fs.existsSync(videoDir)) {
    fs.mkdirSync(videoDir, { recursive: true });
  }

  console.log(`[Playwright Trial ${trialNum}] Iniciando Chrome...`);
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
  });

  const contextOptions = {
    viewport: { width: 1280, height: 720 },
  };

  if (recordVideo) {
    contextOptions.recordVideo = { dir: videoDir, size: { width: 1280, height: 720 } };
  }

  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();

  let videoFile = null;

  try {
    console.log(`[Playwright Trial ${trialNum}] Acessando /login...`);
    await page.goto('http://127.0.0.1:3000/login', { waitUntil: 'networkidle' });

    console.log(`[Playwright Trial ${trialNum}] Preenchendo credenciais...`);
    await page.fill('#fieldnode-login-username', 'admin');
    await page.fill('#fieldnode-login-password', 'senha-admin-s10');
    await page.click('button[type="submit"]');

    console.log(`[Playwright Trial ${trialNum}] Aguardando redirecionamento para /dashboard...`);
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    console.log(`[Playwright Trial ${trialNum}] Abrindo assistente de campo (ChatFAB)...`);
    // O botão do FAB tem classe fixed bottom-24 / bottom-6
    const fabButton = page.locator('button:has-text("assistente"), button[aria-expanded]');
    await fabButton.first().click();

    await page.waitForSelector('#chat-machine-select', { timeout: 5000 });
    await page.selectOption('#chat-machine-select', machineId);

    console.log(`[Playwright Trial ${trialNum}] Clicando em analisar máquina...`);
    await page.click('button:has-text("analisar máquina")');

    console.log(`[Playwright Trial ${trialNum}] Aguardando Prescrição Operacional...`);
    await page.waitForSelector('h2:has-text("Prescrição Operacional")', { timeout: 10000 });

    console.log(`[Playwright Trial ${trialNum}] Verificando campo de outcome...`);
    const outcomeInput = page.locator('#decision-outcome');
    await outcomeInput.waitFor({ state: 'visible', timeout: 5000 });

    console.log(`[Playwright Trial ${trialNum}] Digitando observação no outcome...`);
    await outcomeInput.fill(outcomeText);
    await page.waitForTimeout(500);

    console.log(`[Playwright Trial ${trialNum}] Clicando em "Aprovar ação"...`);
    await page.click('button:has-text("Aprovar ação")');

    console.log(`[Playwright Trial ${trialNum}] Aguardando atualização para status APROVADA...`);
    const approvedBadge = page.locator('span:has-text("APROVADA")');
    await approvedBadge.waitFor({ state: 'visible', timeout: 10000 });

    const registeredOutcome = page.locator('p:has-text("Observação registrada:")');
    await registeredOutcome.waitFor({ state: 'visible', timeout: 5000 });

    console.log(`[Playwright Trial ${trialNum}] SUCESSO! Aprovado no dashboard com status APROVADA e outcome exibido.`);

    const screenshotPath = path.resolve(__dirname, `../artifacts/s10/ensaio-0${trialNum}-dashboard.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`[Playwright Trial ${trialNum}] Screenshot salvo em:`, screenshotPath);

    await page.waitForTimeout(1000); // 1s extra para vídeo
    return { status: 'ok', screenshot: screenshotPath };
  } catch (err) {
    console.error(`[Playwright Trial ${trialNum}] Erro durante execução:`, err);
    throw err;
  } finally {
    if (recordVideo && page.video()) {
      videoFile = await page.video().path();
    }
    await context.close();
    await browser.close();

    if (videoFile) {
      const targetVideoPath = path.resolve(videoDir, `ensaio-0${trialNum}-closed-loop.webm`);
      if (fs.existsSync(videoFile)) {
        fs.copyFileSync(videoFile, targetVideoPath);
        console.log(`[Playwright Trial ${trialNum}] Vídeo salvo oficialmente em:`, targetVideoPath);
      }
    }
  }
}

if (require.main === module) {
  const trialNum = parseInt(process.argv[2] || '1', 10);
  const recordVideo = process.argv.includes('--video');
  const outcomeText = `Ensaio ${trialNum}: Aprovação realizada durante a demonstração oficial; intervenção mecânica não executada.`;
  runUiApproval({ trialNum, outcomeText, recordVideo })
    .then((res) => {
      console.log('Resultado:', res);
      process.exit(0);
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}

module.exports = { runUiApproval };

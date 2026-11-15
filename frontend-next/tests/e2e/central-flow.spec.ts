import { execFileSync } from 'node:child_process';
import crypto from 'node:crypto';
import { test, expect } from '@playwright/test';

type PreparedFlow = {
  token: string;
  machine_code: string;
  event_id: string;
  decision_id: string;
  priority_band: string;
  origin: string;
};

function prepareFlow(): PreparedFlow {
  const runId = crypto.randomBytes(6).toString('hex');
  const output = execFileSync(
    'docker',
    ['compose', 'exec', '-T', 'web', 'python', 'manage.py', 'e2e_prepare_central_flow', '--run-id', runId],
    { cwd: process.cwd().replace(/[\\/]frontend-next$/, ''), encoding: 'utf8' },
  );
  const line = output.split(/\r?\n/).find((candidate) => candidate.trim().startsWith('{'));
  if (!line) throw new Error(`Preparação E2E não retornou JSON: ${output}`);
  return JSON.parse(line) as PreparedFlow;
}

test('fluxo central: leitura crítica, P1, decisão, aprovação, desfecho e auditoria', async ({ page, request }) => {
  const flow = prepareFlow();
  expect(flow.origin).toBe('simulado_e2e');
  expect(flow.priority_band).toBe('P1');

  const eventResponse = await request.get(`http://127.0.0.1:8000/api/events/${flow.event_id}/`, {
    headers: { Authorization: `Token ${flow.token}` },
  });
  expect(eventResponse.ok()).toBeTruthy();
  const event = await eventResponse.json();
  expect(event.id).toBe(flow.event_id);
  expect(event.severidade).toBe('CRITICO');

  await page.context().addCookies([{
    name: 'fieldnode_session', value: flow.token, domain: '127.0.0.1', path: '/',
  }]);
  await page.goto(`/decisoes?decision=${flow.decision_id}`, { waitUntil: 'domcontentloaded', timeout: 20_000 });

  const selected = page.getByTestId('decision-detail');
  await expect(selected).toBeVisible();
  await expect(selected).toContainText(flow.machine_code);
  await expect(selected).toContainText('CRITICO');
  await expect(page.getByTestId('decision-status')).toHaveText('Pendente');

  const outcome = `S3-T11 E2E ${flow.machine_code}: resultado informado para a execução ${flow.event_id}.`;
  await page.getByTestId('decision-outcome').fill(outcome);
  await page.getByTestId('decision-action-APROVADA').click();

  await expect.poll(async () => {
    const response = await request.get(`http://127.0.0.1:8000/api/decisions/${flow.decision_id}/`, {
      headers: { Authorization: `Token ${flow.token}` },
    });
    return (await response.json()).status;
  }).toBe('APROVADA');
  await page.reload();
  await expect(page.getByTestId('decision-status')).toHaveText('Aprovada');

  await page.getByTestId('decision-outcome').fill(outcome);
  await page.getByTestId('decision-action-EXECUTADA').click();
  await expect.poll(async () => {
    const response = await request.get(`http://127.0.0.1:8000/api/decisions/${flow.decision_id}/`, {
      headers: { Authorization: `Token ${flow.token}` },
    });
    return (await response.json()).status;
  }).toBe('EXECUTADA');
  await page.reload();

  await expect(page.getByTestId('decision-status')).toHaveText('Executada');
  await page.getByRole('button', { name: new RegExp(flow.machine_code) }).click();
  await expect(page.getByTestId('decision-status')).toHaveText('Executada');
  await expect(selected).toContainText(outcome);
  await expect(page.getByTestId('decision-audit')).toContainText('Aprovada');
  await expect(page.getByTestId('decision-audit')).toContainText('Execução registrada');

  const persisted = await request.get(`http://127.0.0.1:8000/api/decisions/${flow.decision_id}/`, {
    headers: { Authorization: `Token ${flow.token}` },
  });
  const detail = await persisted.json();
  expect(detail.status).toBe('EXECUTADA');
  expect(detail.outcome_texto).toBe(outcome);
  expect(detail.historico.map((item: { action: string }) => item.action)).toEqual(
    expect.arrayContaining(['decision.approve', 'decision.execute']),
  );
});

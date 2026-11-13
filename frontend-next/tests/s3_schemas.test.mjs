import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import test from 'node:test';

const require = createRequire(import.meta.url);
const ts = require('typescript');
const zodRequire = createRequire(new URL('../package.json', import.meta.url));

async function loadSchema(relativePath, exportNames) {
  const source = await readFile(new URL(`../src/schemas/${relativePath}`, import.meta.url), 'utf8');
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const module = { exports: {} };
  vm.runInNewContext(compiled, {
    exports: module.exports,
    require: (name) => zodRequire(name),
  });
  return Object.fromEntries(exportNames.map((name) => [name, module.exports[name]]));
}

const { EventoPageSchema } = await loadSchema('eventos.ts', ['EventoPageSchema']);
const { DecisaoPageSchema } = await loadSchema('decisoes.ts', ['DecisaoPageSchema']);
const { SaudeMaquinaSchema } = await loadSchema('saude.ts', ['SaudeMaquinaSchema']);
const { LeituraTelemetriaSchema } = await loadSchema('telemetria.ts', ['LeituraTelemetriaSchema']);

test('schemas S3 aceitam contratos paginados e saúde vazia reais', () => {
  const event = {
    id: 'f4a94631-04e9-4763-a7b2-646d5e48f8ee', machine: '91bb0aef-b0f8-4b44-9859-5fb626e42544',
    machine_id: '91bb0aef-b0f8-4b44-9859-5fb626e42544', machine_external_code: 'FN-01',
    leitura_origem: null, leitura_origem_id: null, tipo: 'TEMP_ALTA', severidade: 'ATENCAO', status: 'ABERTO',
    trust_score_herdado: null, evidence_quality: 'insuficiente', needs_verification: true, priority_score: '0.7500',
    criado_em: '2026-11-13T12:00:00Z', dados_contexto: {},
  };
  const page = { count: 1, page: 1, page_size: 20, pages: 1, next: null, previous: null, results: [event] };
  const parsedEventPage = EventoPageSchema.safeParse(page);
  assert.equal(parsedEventPage.success, true);
  if (parsedEventPage.success) assert.equal(parsedEventPage.data.results[0].priority_score, 0.75);
  assert.equal(EventoPageSchema.safeParse({ ...page, results: [{ ...event, severidade: 'URGENTE' }] }).success, false);

  const decision = {
    id: event.id, machine: event.machine, machine_external_code: 'FN-01', event: null, texto: 'Revisar leitura',
    acao_recomendada: 'Verificar sensor', severidade: 'NORMAL', confianca: null, status: 'PENDENTE',
    criado_em: '2026-11-13T12:00:00Z', decidido_por: null, decidido_por_username: null,
    decidido_em: null, outcome_texto: null, metodologia: null,
  };
  assert.equal(DecisaoPageSchema.safeParse({ ...page, results: [decision] }).success, true);
  assert.equal(DecisaoPageSchema.safeParse({ ...page, results: [{ ...decision, status: 'UNKNOWN' }] }).success, false);

  const health = {
    machine_id: event.machine, external_code: 'FN-01', status: 'sem_dados', trust_score_medio: null,
    ultima_atualizacao: null, leituras_analisadas: 0, sinais_de_alerta: {},
  };
  assert.equal(SaudeMaquinaSchema.safeParse(health).success, true);
  assert.equal(SaudeMaquinaSchema.safeParse({ ...health, leituras_analisadas: -1 }).success, false);
  assert.equal(LeituraTelemetriaSchema.safeParse({
    maquina_id: 'FN-01', temperatura: 70, vibracao: 0.3, rpm: 1800,
    timestamp: null, data_origin: null,
  }).success, true);
});

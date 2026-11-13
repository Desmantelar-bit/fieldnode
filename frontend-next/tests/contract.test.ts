import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import test from 'node:test';

const frontendRoot = new URL('../', import.meta.url);
const repoRoot = new URL('../../', import.meta.url);
const require = createRequire(import.meta.url);
const ts = require('typescript');
const sourcePath = new URL('src/lib/metricThresholds.ts', frontendRoot);
const fixturesPath = new URL('contracts/fixtures/classificacao.json', repoRoot);
const contractPath = new URL('contracts/severity.v1.json', repoRoot);
const attentionContractPath = new URL('contracts/attention.v1.json', repoRoot);

const source = await readFile(sourcePath, 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
}).outputText;
const moduleExports = {} as { classifyMetric: (key: string, value: number) => string };
vm.runInNewContext(compiled, { exports: moduleExports, Number, RangeError });
const fixtures = JSON.parse(await readFile(fixturesPath, 'utf8')) as Array<Record<string, unknown>>;
const contract = JSON.parse(await readFile(contractPath, 'utf8')) as {
  severity_order: string[];
};

test('frontend severity classification matches shared golden boundaries', () => {
  for (const fixture of fixtures) {
    const caseId = String(fixture.id);
    if (fixture.expected_error === 'range') {
      const metric: 'temperatura' | 'vibracao' = caseId.startsWith('temperatura_') ? 'temperatura' : 'vibracao';
      assert.throws(
        () => moduleExports.classifyMetric(metric, Number(fixture[metric])),
        RangeError,
        `frontend aceitou caso inválido ${caseId}`,
      );
      continue;
    }
    const temperatureSeverity = moduleExports.classifyMetric('temperatura', Number(fixture.temperatura));
    const vibrationSeverity = moduleExports.classifyMetric('vibracao', Number(fixture.vibracao));
    assert.equal(
      temperatureSeverity,
      fixture.severidade_temperatura,
      `frontend temperatura, caso ${caseId}: esperado=${fixture.severidade_temperatura} obtido=${temperatureSeverity}`,
    );
    assert.equal(
      vibrationSeverity,
      fixture.severidade_vibracao,
      `frontend vibração, caso ${caseId}: esperado=${fixture.severidade_vibracao} obtido=${vibrationSeverity}`,
    );
    const actual = [temperatureSeverity, vibrationSeverity].sort(
      (left, right) => contract.severity_order.indexOf(left) - contract.severity_order.indexOf(right),
    ).at(-1);
    assert.equal(actual, fixture.severidade, `frontend consolidada, caso ${caseId}`);
  }
});

test('attention priority follows the shared heuristic boundaries and critical override', async () => {
  const attentionSource = await readFile(new URL('src/lib/attentionPriority.ts', frontendRoot), 'utf8');
  const attentionContract = JSON.parse(await readFile(attentionContractPath, 'utf8'));
  const attentionModule = {} as { classifyAttention: (score: number | null, severity: string) => string | null };
  const attentionCompiled = ts.transpileModule(attentionSource, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  vm.runInNewContext(attentionCompiled, {
    exports: attentionModule,
    require: () => ({ default: attentionContract }),
    Number,
  });
  const classify = attentionModule.classifyAttention;
  assert.equal(classify(0.2999, 'ATENCAO'), 'P3');
  assert.equal(classify(0.30, 'ATENCAO'), 'P2');
  assert.equal(classify(0.5999, 'ATENCAO'), 'P2');
  assert.equal(classify(0.60, 'ATENCAO'), 'P1');
  assert.equal(classify(0.9, 'ATENCAO'), 'P1');
  assert.equal(classify(0.01, 'CRITICO'), 'P1');
  assert.equal(classify(null, 'ATENCAO'), null);
  assert.equal(classify(Number.NaN, 'ATENCAO'), null);
  assert.equal(classify(-0.01, 'ATENCAO'), null);
  assert.equal(classify(1.01, 'ATENCAO'), null);
});

test('every known trust factor has a nonempty Portuguese explanation', async () => {
  const factorsSource = await readFile(new URL('src/lib/trustFactors.ts', frontendRoot), 'utf8');
  const factorsModule = {} as {
    trustFactorLabels: Record<string, { title: string; description: string }>;
    describeTrustFactor: (code: string) => { title: string; description: string };
  };
  const factorsCompiled = ts.transpileModule(factorsSource, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  vm.runInNewContext(factorsCompiled, { exports: factorsModule });
  for (const code of Object.keys(factorsModule.trustFactorLabels)) {
    const definition = factorsModule.describeTrustFactor(code);
    assert.ok(definition.title.trim());
    assert.ok(definition.description.trim());
  }
  assert.equal(factorsModule.describeTrustFactor('NOVO_CODIGO').title, 'Outro fator (NOVO_CODIGO)');
});

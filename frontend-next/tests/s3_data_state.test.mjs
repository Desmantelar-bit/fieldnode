import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import vm from 'node:vm';
import test from 'node:test';

const require = createRequire(new URL('../package.json', import.meta.url));
const ts = require('typescript');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const source = await readFile(new URL('../src/components/DataStateBoundary.tsx', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, jsx: ts.JsxEmit.ReactJSX },
}).outputText;
const element = (text) => React.createElement('div', null, text);
const dependencyMap = {
  react: React,
  'react/jsx-runtime': require('react/jsx-runtime'),
  'lucide-react': { AlertTriangle: () => element('alert'), WifiOff: () => element('offline-icon') },
  '@/components/ui/FeedbackStates': {
    EmptyState: ({ title, message }) => React.createElement('div', null, title, message),
    ErrorState: ({ title, message, onRetry }) => React.createElement('div', null, title, message,
      onRetry ? React.createElement('button', { onClick: onRetry }, 'retry') : null),
  },
  '@/components/SkeletonGrid': { SkeletonGrid: () => element('skeleton') },
  '@/components/SimulatedBadge': { SimulatedBadge: () => element('SIMULADO') },
};
const module = { exports: {} };
vm.runInNewContext(compiled, {
  exports: module.exports,
  require: (name) => dependencyMap[name] ?? require(name),
});
const { DataStateBoundary } = module.exports;
const render = (props) => renderToStaticMarkup(React.createElement(DataStateBoundary, props));

test('DataStateBoundary distinguishes each of the seven requested states', () => {
  assert.match(render({ state: 'loading', children: 'payload' }), /skeleton/);
  assert.match(render({ state: 'ok', children: 'payload' }), /payload/);
  assert.match(render({ state: 'ok', simulated: true, children: 'payload' }), /SIMULADO/);
  assert.match(render({ state: 'sem_historico', children: 'payload' }), /Sem histórico suficiente/);
  const stale = render({ state: 'desatualizado', simulated: true, children: 'last-known' });
  assert.match(stale, /last-known/);
  assert.match(stale, /SIMULADO/);
  assert.match(stale, /atrasada/);
  assert.match(render({ state: 'offline', children: 'payload' }), /Sem conexão com a API/);
  const failed = render({ state: 'erro', children: 'payload', onRetry: () => undefined });
  assert.match(failed, /Falha ao carregar dados/);
  assert.match(failed, /retry/);
  assert.doesNotMatch(failed, /payload/);
  const invalid = render({ state: 'invalido', children: 'invalid-payload' });
  assert.match(invalid, /Resposta inválida/);
  assert.doesNotMatch(invalid, /invalid-payload/);
});

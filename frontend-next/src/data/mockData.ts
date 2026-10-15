/**
 * mockData.ts — Dados demonstrativos para fallbacks visuais e sparklines sem dados reais.
 *
 * REGRAS:
 * - Nunca substituir chamadas reais à API por estes dados.
 * - Usar apenas quando a API não retornar dados ou para sparklines de demonstração.
 * - Não importar no telemetryService.
 */

/** Série de RPM para sparkline demonstrativa */
export const mockRpmSeries = [
  { valor: 1750, label: 'Ponto 1' }, { valor: 1800, label: 'Ponto 2' }, { valor: 1820, label: 'Ponto 3' },
  { valor: 1790, label: 'Ponto 4' }, { valor: 1850, label: 'Ponto 5' }, { valor: 1820, label: 'Ponto 6' },
];

/** Série de temperatura para sparkline demonstrativa */
export const mockTemperaturaSeries = [
  { valor: 72, label: 'Ponto 1' }, { valor: 74, label: 'Ponto 2' }, { valor: 76, label: 'Ponto 3' },
  { valor: 79, label: 'Ponto 4' }, { valor: 82, label: 'Ponto 5' }, { valor: 78, label: 'Ponto 6' },
];

/** Série de vibração para sparkline demonstrativa */
export const mockVibracaoSeries = [
  { valor: 1.8, label: 'Ponto 1' }, { valor: 2.0, label: 'Ponto 2' }, { valor: 1.9, label: 'Ponto 3' },
  { valor: 2.2, label: 'Ponto 4' }, { valor: 2.1, label: 'Ponto 5' }, { valor: 2.1, label: 'Ponto 6' },
];

/** Resumo de frota para overlay do mapa quando API não retornar dados */
export const mockFleetSummary = {
  total:    12,
  operando: 9,
  atencao:  2,
  paradas:  1,
} as const;

/** Tendência operacional para gráfico de linha no dashboard */
export const mockTrendSeries = [
  { hora: '06h', rpm: 1720, temp: 70, vib: 1.7 },
  { hora: '08h', rpm: 1780, temp: 73, vib: 1.9 },
  { hora: '10h', rpm: 1820, temp: 76, vib: 2.0 },
  { hora: '12h', rpm: 1800, temp: 79, vib: 2.1 },
  { hora: '14h', rpm: 1850, temp: 82, vib: 2.2 },
  { hora: '16h', rpm: 1820, temp: 78, vib: 2.0 },
  { hora: '18h', rpm: 1760, temp: 74, vib: 1.8 },
];

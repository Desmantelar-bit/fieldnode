type ThemeTokenKey =
  | 'background'
  | 'foreground'
  | 'panel'
  | 'line'
  | 'statusNormal'
  | 'statusAtencao'
  | 'statusCritico'
  | 'statusNeutro'
  | 'chartNormalStroke'
  | 'chartNormalFill'
  | 'chartAtencaoStroke'
  | 'chartAtencaoFill'
  | 'chartCriticoStroke'
  | 'chartCriticoFill'
  | 'chartBlueStroke'
  | 'chartBlueFill'
  | 'chartVioletStroke'
  | 'chartVioletFill'
  | 'chartGrid'
  | 'chartSurface'
  | 'chartPointStroke'
  | 'chartTransparent'
  | 'glowNormal'
  | 'glowNormalStrong'
  | 'overlayDebug';

const tokenNames: Record<ThemeTokenKey, string> = {
  background:         '--background',
  foreground:         '--foreground',
  panel:              '--panel',
  line:               '--line',
  statusNormal:       '--status-normal',
  statusAtencao:      '--status-atencao',
  statusCritico:      '--status-critico',
  statusNeutro:       '--status-neutro',
  chartNormalStroke:  '--chart-normal-stroke',
  chartNormalFill:    '--chart-normal-fill',
  chartAtencaoStroke: '--chart-atencao-stroke',
  chartAtencaoFill:   '--chart-atencao-fill',
  chartCriticoStroke: '--chart-critico-stroke',
  chartCriticoFill:   '--chart-critico-fill',
  chartBlueStroke:    '--chart-blue-stroke',
  chartBlueFill:      '--chart-blue-fill',
  chartVioletStroke:  '--chart-violet-stroke',
  chartVioletFill:    '--chart-violet-fill',
  chartGrid:          '--chart-grid',
  chartSurface:       '--chart-surface',
  chartPointStroke:   '--chart-point-stroke',
  chartTransparent:   '--chart-transparent',
  glowNormal:         '--glow-normal',
  glowNormalStrong:   '--glow-normal-strong',
  overlayDebug:       '--overlay-debug',
};

export function cssVar(key: ThemeTokenKey) {
  return `var(${tokenNames[key]})`;
}

export function readCssVar(key: ThemeTokenKey) {
  if (typeof window === 'undefined') return '';
  const value = window
    .getComputedStyle(document.documentElement)
    .getPropertyValue(tokenNames[key])
    .trim();
  if (!value) throw new Error(`Design token CSS ausente: ${tokenNames[key]}`);
  return value;
}

export const chartColors = {
  normal: {
    stroke: cssVar('chartNormalStroke'),
    fill:   cssVar('chartNormalFill'),
    label:  'Normal',
  },
  atencao: {
    stroke: cssVar('chartAtencaoStroke'),
    fill:   cssVar('chartAtencaoFill'),
    label:  'Atenção',
  },
  critico: {
    stroke: cssVar('chartCriticoStroke'),
    fill:   cssVar('chartCriticoFill'),
    label:  'Crítico',
  },
  blue: {
    stroke: cssVar('chartBlueStroke'),
    fill:   cssVar('chartBlueFill'),
    label:  'Análise',
  },
  violet: {
    stroke: cssVar('chartVioletStroke'),
    fill:   cssVar('chartVioletFill'),
    label:  'Tendência',
  },
  grid:        cssVar('chartGrid'),
  surface:     cssVar('chartSurface'),
  pointStroke: cssVar('chartPointStroke'),
  transparent: cssVar('chartTransparent'),
} as const;

export function getStatusColor(status: 'operando' | 'parada' | string) {
  if (status === 'operando') return readCssVar('statusNormal');
  if (status === 'parada')   return readCssVar('statusAtencao');
  return readCssVar('statusCritico');
}

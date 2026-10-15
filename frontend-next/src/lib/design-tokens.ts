// Tokens de classe Tailwind — fonte única de verdade para composição de componentes.
// Não alterar a API pública (nomes exportados) sem atualizar todos os consumidores.

export const glassCard = 'glass-panel rounded-2xl';
export const glassPill = 'glass-panel rounded-full';
export const surfaceCard = 'surface-panel rounded-2xl';
export const lightCard = 'rounded-2xl bg-[var(--surface-1)] text-[var(--text-1)] shadow-[var(--shadow-card)]';

// Tipografia e KPIs
export const kpiNumber = 'stat-value text-4xl font-bold text-[var(--text-1)]';
export const kpiLabel = 'text-[11px] font-semibold uppercase tracking-[0.06em] text-[var(--text-3)]';
export const sectionEyebrow = 'text-[11px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]';
export const fieldLabel = 'text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]';

// Ações e controles compartilhados
export const primaryButton =
  'btn-brand inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] disabled:cursor-not-allowed';

export const secondaryButton =
  'inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-[var(--panel-glass-mid)] px-5 py-2.5 text-sm font-semibold text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.97]';

// Cores semânticas para texto
export const statusColor = {
  normal:  'text-[color:var(--status-normal)]',
  atencao: 'text-[color:var(--status-atencao)]',
  critico: 'text-[color:var(--status-critico)]',
} as const;

// Cores para séries de gráfico e sparklines
export const sparklineColor = {
  normal:  'var(--chart-normal-stroke)',
  atencao: 'var(--chart-atencao-stroke)',
  critico: 'var(--chart-critico-stroke)',
  blue:    'var(--chart-blue-stroke)',
  violet:  'var(--chart-violet-stroke)',
} as const;

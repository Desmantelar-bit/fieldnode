export const glassCard = 'glass-panel rounded-3xl';
export const glassPill = 'glass-panel rounded-full';
export const lightCard = 'rounded-3xl bg-slate-50 text-slate-950 shadow-[0_24px_80px_rgba(0,0,0,0.32)]';

// Tipografia e KPIs
export const kpiNumber = 'text-5xl font-bold tracking-tighter text-white';
export const kpiLabel = 'text-xs uppercase tracking-wide text-slate-400';
export const sectionEyebrow = 'text-[11px] font-semibold uppercase tracking-[0.18em] text-accent';
export const fieldLabel = 'text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500';

// Ações e controles compartilhados
export const primaryButton = 'inline-flex min-h-11 items-center justify-center gap-2 rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-950/10 transition hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-950 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.97]';
export const secondaryButton = 'inline-flex min-h-11 items-center justify-center gap-2 rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-900 transition hover:border-slate-950 hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-950 disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.97]';

// Cores semânticas
export const statusColor = {
  normal: 'text-lime-400',
  atencao: 'text-amber-400',
  critico: 'text-orange-500',
} as const;

// Cores semânticas reservadas para séries de tendência e sparklines.
export const sparklineColor = {
  normal: 'var(--status-normal)',
  atencao: 'var(--status-atencao)',
  critico: 'var(--status-critico)',
} as const;

export const glassCard = 'border border-white/10 bg-slate-900/45 shadow-glass backdrop-blur-xl rounded-3xl';
export const glassPill = 'border border-white/10 bg-slate-950/60 shadow-glass backdrop-blur-xl rounded-full';
export const kpiNumber = 'text-4xl font-semibold tracking-tight text-white sm:text-5xl';
export const kpiLabel = 'text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400';
export const surfacePage = 'bg-[image:var(--surface-page)]';
export const statusColor = {
  normal: 'text-status-normal',
  atencao: 'text-status-atencao',
  critico: 'text-status-critico',
} as const;
export const statusSurface = {
  normal: 'border-status-normal/25 bg-status-normal/10',
  atencao: 'border-status-atencao/25 bg-status-atencao/10',
  critico: 'border-status-critico/25 bg-status-critico/10',
} as const;
export const sparklineColor = {
  normal: 'var(--status-normal)',
  atencao: 'var(--status-atencao)',
  critico: 'var(--status-critico)',
} as const;

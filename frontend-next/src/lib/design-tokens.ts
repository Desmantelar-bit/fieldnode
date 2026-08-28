// Superfícies Glassmorphism
export const glassCard = 'bg-slate-900/40 backdrop-blur-xl border border-white/10 rounded-3xl';
export const glassPill = 'bg-slate-900/50 backdrop-blur-md border border-white/10 rounded-full';

// Tipografia e KPIs
export const kpiNumber = 'text-5xl font-bold tracking-tighter text-white';
export const kpiLabel = 'text-xs uppercase tracking-wide text-slate-400';

// Cores Semânticas
export const statusColor = {
  normal: 'text-lime-400',
  atencao: 'text-amber-400',
  critico: 'text-orange-500',
} as const;

// Cores semânticas reservadas para séries de tendência e sparklines.
export const sparklineColor = {
  normal: '#CCFF00',
  atencao: '#FBBF24',
  critico: '#FF5E00',
} as const;

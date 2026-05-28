import type { ReactNode } from 'react';

type StatusTone = 'normal' | 'warning' | 'critical' | 'muted';

const toneClasses: Record<StatusTone, string> = {
  normal: 'border-emerald-300/25 bg-emerald-300/10 text-emerald-200',
  warning: 'border-amber-300/25 bg-amber-300/10 text-amber-200',
  critical: 'border-red-300/25 bg-red-300/10 text-red-200',
  muted: 'border-white/10 bg-white/5 text-slate-300',
};

export function StatusBadge({ children, tone = 'muted' }: { children: ReactNode; tone?: StatusTone }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] ${toneClasses[tone]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {children}
    </span>
  );
}

export function riskTone(risk?: string): StatusTone {
  const normalized = risk
    ?.normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase();
  if (normalized === 'CRITICO') return 'critical';
  if (normalized === 'ATENCAO') return 'warning';
  if (normalized === 'NORMAL') return 'normal';
  return 'muted';
}

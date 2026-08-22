import type { ReactNode } from 'react';

type StatusTone = 'normal' | 'warning' | 'critical' | 'muted';

const toneClasses: Record<StatusTone, string> = {
  normal: 'border-status-normal/25 bg-status-normal/10 text-status-normal',
  warning: 'border-status-atencao/25 bg-status-atencao/10 text-status-atencao',
  critical: 'border-status-critico/25 bg-status-critico/10 text-status-critico',
  muted: 'border-field-border bg-field-glass text-field-text3',
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

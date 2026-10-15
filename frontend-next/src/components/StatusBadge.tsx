import type { ReactNode } from 'react';

type StatusTone = 'normal' | 'warning' | 'critical' | 'muted';

const toneClasses: Record<StatusTone, string> = {
  normal:   'border-[color:var(--status-normal)]/25 bg-[color:var(--status-normal)]/10 text-[color:var(--status-normal)]',
  warning:  'border-[color:var(--status-atencao)]/25 bg-[color:var(--status-atencao)]/10 text-[color:var(--status-atencao)]',
  critical: 'border-[color:var(--status-critico)]/25 bg-[color:var(--status-critico)]/10 text-[color:var(--status-critico)]',
  muted:    'border-[var(--line)] bg-[var(--panel-glass-mid)] text-[var(--text-3)]',
};

export function StatusBadge({
  children,
  tone = 'muted',
}: {
  children: ReactNode;
  tone?: StatusTone;
}) {
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.1em] ${toneClasses[tone]}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
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
  if (normalized === 'ALERTA')  return 'critical';
  if (normalized === 'NORMAL')  return 'normal';
  return 'muted';
}

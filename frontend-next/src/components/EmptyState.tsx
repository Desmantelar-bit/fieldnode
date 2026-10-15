import { AlertTriangle, Inbox } from 'lucide-react';

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <section className="metric-card border border-dashed border-[var(--line)] py-12 text-center">
      <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--panel-glass-strong)] text-[var(--text-3)]">
        <Inbox size={20} aria-hidden="true" />
      </div>
      <h2 className="mt-4 text-sm font-bold text-[var(--text-1)]">{title}</h2>
      <p className="mx-auto mt-2 max-w-sm text-xs leading-relaxed text-[var(--text-3)]">{message}</p>
    </section>
  );
}

const ERROR_VARIANT = {
  api: {
    label: 'API indisponível',
    border: 'border-[color:var(--status-critico)]/20',
    bg:     'bg-[color:var(--status-critico)]/5',
    text:   'text-[color:var(--status-critico)]',
    sub:    'text-[color:var(--status-critico)]/70',
  },
  gps: {
    label: 'GPS ausente',
    border: 'border-[color:var(--status-atencao)]/20',
    bg:     'bg-[color:var(--status-atencao)]/5',
    text:   'text-[color:var(--status-atencao)]',
    sub:    'text-[color:var(--status-atencao)]/70',
  },
  insufficient: {
    label: 'Dados insuficientes',
    border: 'border-[var(--line)]',
    bg:     'bg-[var(--panel-glass-mid)]',
    text:   'text-[var(--text-3)]',
    sub:    'text-[var(--text-3)]/70',
  },
} as const;

type ErrorVariant = keyof typeof ERROR_VARIANT;

export function ErrorState({
  title,
  message,
  variant = 'api',
}: {
  title: string;
  message: string;
  variant?: ErrorVariant;
}) {
  const v = ERROR_VARIANT[variant];
  return (
    <section className={`metric-card border ${v.border} ${v.bg}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle size={18} className={`mt-0.5 shrink-0 ${v.text}`} aria-hidden="true" />
        <div>
          <p className={`text-[10px] font-semibold uppercase tracking-[0.1em] ${v.text}`}>
            {v.label}
          </p>
          <h2 className="mt-1.5 text-sm font-bold text-[var(--text-1)]">{title}</h2>
          <p className={`mt-1.5 text-xs leading-relaxed ${v.sub}`}>{message}</p>
        </div>
      </div>
    </section>
  );
}

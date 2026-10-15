import { AlertTriangle, Inbox } from 'lucide-react';

type EmptyStateProps = {
  title?: string;
  message?: string;
  mensagem?: string;
};

type ErrorStateProps = EmptyStateProps & {
  variant?: 'api' | 'gps' | 'insufficient';
  onRetry?: () => void;
};

const ERROR_VARIANT = {
  api: {
    label:  'API indisponível',
    border: 'border-[color:var(--status-critico)]/20',
    bg:     'bg-[color:var(--status-critico)]/5',
    text:   'text-[color:var(--status-critico)]',
    sub:    'text-[color:var(--status-critico)]/70',
  },
  gps: {
    label:  'GPS ausente',
    border: 'border-[color:var(--status-atencao)]/20',
    bg:     'bg-[color:var(--status-atencao)]/5',
    text:   'text-[color:var(--status-atencao)]',
    sub:    'text-[color:var(--status-atencao)]/70',
  },
  insufficient: {
    label:  'Dados insuficientes',
    border: 'border-[var(--line)]',
    bg:     'bg-[var(--panel-glass-mid)]',
    text:   'text-[var(--text-3)]',
    sub:    'text-[var(--text-3)]/70',
  },
} as const;

export function LoadingState({ mensagem = 'Carregando dados...' }: { mensagem?: string }) {
  return (
    <section className="flex h-full min-h-[200px] flex-col items-center justify-center gap-3 p-8 text-[var(--text-3)]">
      <span className="h-7 w-7 animate-spin rounded-full border-2 border-[color:var(--ui-accent)] border-t-transparent" />
      <p className="text-xs font-semibold uppercase tracking-[0.1em]">{mensagem}</p>
    </section>
  );
}

export function EmptyState({
  title = 'Nenhum dado encontrado.',
  message,
  mensagem,
}: EmptyStateProps) {
  return (
    <section className="metric-card py-10 text-center">
      <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--panel-glass-strong)] text-[var(--text-3)]">
        <Inbox size={18} aria-hidden="true" />
      </div>
      <h2 className="mt-3 text-sm font-bold text-[var(--text-1)]">{title}</h2>
      <p className="mx-auto mt-1.5 max-w-sm text-xs leading-relaxed text-[var(--text-3)]">
        {mensagem || message || 'Nenhum dado encontrado.'}
      </p>
    </section>
  );
}

export function ErrorState({
  title = 'Ocorreu um erro inesperado.',
  message,
  mensagem,
  variant = 'api',
  onRetry,
}: ErrorStateProps) {
  const v = ERROR_VARIANT[variant];
  return (
    <section className={`metric-card border ${v.border} ${v.bg}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle size={17} className={`mt-0.5 shrink-0 ${v.text}`} aria-hidden="true" />
        <div className="min-w-0">
          <p className={`text-[10px] font-semibold uppercase tracking-[0.1em] ${v.text}`}>
            {v.label}
          </p>
          <h2 className="mt-1.5 text-sm font-bold text-[var(--text-1)]">{title}</h2>
          <p className={`mt-1.5 text-xs leading-relaxed ${v.sub}`}>
            {mensagem || message || 'Ocorreu um erro inesperado.'}
          </p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="mt-3 rounded-xl bg-[var(--panel-glass-mid)] px-4 py-2 text-xs font-semibold text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] active:scale-95"
            >
              Tentar novamente
            </button>
          )}
        </div>
      </div>
    </section>
  );
}

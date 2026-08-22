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
    label: 'API indisponivel',
    icon: '!',
    border: 'border-red-300/20',
    bg: 'bg-red-300/10',
    labelColor: 'text-red-200',
    messageColor: 'text-red-100/75',
  },
  gps: {
    label: 'GPS ausente',
    icon: 'x',
    border: 'border-amber-300/20',
    bg: 'bg-amber-300/10',
    labelColor: 'text-amber-200',
    messageColor: 'text-amber-100/75',
  },
  insufficient: {
    label: 'Dados insuficientes',
    icon: '~',
    border: 'border-slate-300/20',
    bg: 'bg-slate-300/10',
    labelColor: 'text-slate-400',
    messageColor: 'text-slate-400/75',
  },
} as const;

export function LoadingState({
  mensagem = 'Carregando dados...',
}: {
  mensagem?: string;
}) {
  return (
    <section className="flex h-full min-h-[200px] flex-col items-center justify-center p-8 text-slate-400">
      <span className="mb-4 h-8 w-8 animate-spin rounded-full border-2 border-status-normal border-t-transparent" />
      <p className="text-sm uppercase tracking-[0.18em]">{mensagem}</p>
    </section>
  );
}

export function EmptyState({
  title = 'Nenhum dado encontrado.',
  message,
  mensagem,
}: EmptyStateProps) {
  return (
    <section className="glass-panel rounded-lg border-dashed p-8 text-center">
      <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">Sem dados</p>
      <h2 className="mt-2 text-lg font-semibold text-slate-100">{title}</h2>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-400">
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
    <section className={`rounded-lg border ${v.border} ${v.bg} p-6`}>
      <p className={`text-[11px] font-semibold uppercase tracking-[0.2em] ${v.labelColor}`}>
        {v.icon} {v.label}
      </p>
      <h2 className="mt-2 text-lg font-semibold text-slate-100">{title}</h2>
      <p className={`mt-3 max-w-2xl text-sm leading-6 ${v.messageColor}`}>
        {mensagem || message || 'Ocorreu um erro inesperado.'}
      </p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-md border border-white/10 bg-white/[0.06] px-4 py-2 text-xs font-semibold text-white transition hover:bg-white/[0.1]"
        >
          Tentar novamente
        </button>
      )}
    </section>
  );
}

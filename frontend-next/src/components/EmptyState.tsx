export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <section className="glass-panel rounded-lg border-dashed p-8 text-center">
      <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">Sem dados</p>
      <h2 className="mt-2 text-lg font-semibold text-slate-100">{title}</h2>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-400">{message}</p>
    </section>
  );
}

const ERROR_VARIANT = {
  api: {
    label: 'API indisponivel',
    icon: '✗',
    border: 'border-red-300/20',
    bg: 'bg-red-300/10',
    labelColor: 'text-red-200',
    messageColor: 'text-red-100/75',
  },
  gps: {
    label: 'GPS ausente',
    icon: '⊘',
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
    <section className={`rounded-lg border ${v.border} ${v.bg} p-6`}>
      <p className={`text-[11px] font-semibold uppercase tracking-[0.2em] ${v.labelColor}`}>
        {v.icon} {v.label}
      </p>
      <h2 className="mt-2 text-lg font-semibold text-slate-100">{title}</h2>
      <p className={`mt-3 max-w-2xl text-sm leading-6 ${v.messageColor}`}>{message}</p>
    </section>
  );
}

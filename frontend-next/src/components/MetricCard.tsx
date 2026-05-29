import type { ReactNode } from 'react';

const toneClass = {
  emerald: 'text-emerald-200',
  amber: 'text-amber-200',
  red: 'text-red-200',
  slate: 'text-slate-100',
};

export function MetricCard({
  label,
  value,
  helper,
  tone = 'slate',
}: {
  label: string;
  value: ReactNode;
  helper?: string;
  tone?: keyof typeof toneClass;
}) {
  return (
    <article
      role="group"
      aria-label={label}
      className="glass-panel rounded-lg p-4 sm:p-5 min-h-[5rem]"
    >
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        {label}
      </p>
      <div
        className={`mt-3 text-2xl sm:text-3xl font-semibold tracking-tight ${toneClass[tone]}`}
      >
        {value}
      </div>
      {helper ? <p className="mt-2 text-sm text-slate-400">{helper}</p> : null}
    </article>
  );
}

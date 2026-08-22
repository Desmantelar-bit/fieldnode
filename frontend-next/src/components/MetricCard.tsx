import type { ReactNode } from 'react';

const toneClass = {
  emerald: 'text-status-normal',
  amber: 'text-status-atencao',
  red: 'text-status-critico',
  slate: 'text-field-text1',
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
      className="glass-panel rounded-lg p-4 sm:p-6 min-h-[5rem]"
    >
      <p className="text-[11px] font-semibold uppercase tracking-label text-field-text3">
        {label}
      </p>
      <div className={`mt-3 text-2xl sm:text-3xl font-semibold tracking-title ${toneClass[tone]}`}>
        {value}
      </div>
      {helper ? <p className="mt-2 text-sm text-field-text3">{helper}</p> : null}
    </article>
  );
}

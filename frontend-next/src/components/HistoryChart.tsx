import type { Telemetry } from '@/types/telemetry';

const toneClasses = {
  red: 'fill-red-300/70',
  amber: 'fill-amber-300/70',
  emerald: 'fill-emerald-300/70',
};

export function HistoryChart({
  title,
  readings,
  field,
  suffix = '',
  tone,
}: {
  title: string;
  readings: Telemetry[];
  field: 'temperatura' | 'vibracao' | 'rpm';
  suffix?: string;
  tone: keyof typeof toneClasses;
}) {
  const values = readings.map((reading) => Number(reading[field])).reverse();
  const max = Math.max(...values, 1);

  return (
    <article className="glass-panel rounded-lg p-5">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-sm font-semibold text-slate-200">{title}</h2>
        <span className="font-mono text-xs text-slate-500">
          {values.length} leituras
        </span>
      </div>
      <svg
        viewBox="0 0 240 120"
        className="mt-5 h-40 sm:h-56 w-full rounded-md border border-white/10 bg-black/15 p-4"
        role="img"
        aria-label={title}
        preserveAspectRatio="xMidYMid meet"
      >
        {values.slice(-24).map((value, index) => {
          const height = Math.max((value / max) * 96, 4);
          return (
            <rect
              key={`${field}-${index}`}
              x={index * 10 + 1}
              y={108 - height}
              width="7"
              height={height}
              rx="1.5"
              className={toneClasses[tone]}
            >
              <title>{`${value}${suffix}`}</title>
            </rect>
          );
        })}
      </svg>
    </article>
  );
}

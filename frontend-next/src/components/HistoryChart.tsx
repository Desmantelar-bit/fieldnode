import type { Telemetry } from '@/types/telemetry';

const toneStyles = {
  red: { stroke: '#fca5a5', fill: 'rgba(239,68,68,0.18)', label: 'Crítico' },
  amber: { stroke: '#fcd34d', fill: 'rgba(245,158,11,0.18)', label: 'Atenção' },
  emerald: { stroke: '#6ee7b7', fill: 'rgba(16,185,129,0.18)', label: 'Normal' },
};

const thresholdRanges: Record<string, { alert: number; critical: number; unit: string; higherIsWorse: boolean; min: number; max: number }> = {
  temperatura: { alert: 95, critical: 110, unit: '°C', higherIsWorse: true, min: 0, max: 150 },
  vibracao:    { alert: 0.5, critical: 0.8, unit: 'g', higherIsWorse: true, min: 0, max: 10 },
  rpm:         { alert: 1400, critical: 1200, unit: 'rpm', higherIsWorse: false, min: 0, max: 3000 },
};

const fmt = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });

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
  tone: keyof typeof toneStyles;
}) {
  const points = readings.map((r) => Number(r[field])).reverse();
  if (!points.length) {
    return (
      <article className="glass-panel rounded-lg p-5">
        <h2 className="text-sm font-semibold text-slate-200">{title}</h2>
        <p className="mt-4 text-xs text-slate-500">Sem leituras no período.</p>
      </article>
    );
  }

  const width = 640;
  const height = 220;
  const pad = { top: 24, right: 24, bottom: 32, left: 48 };
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;
  const max = Math.max(...points, 1);
  const min = Math.min(...points, 0);
  const range = max - min || 1;

  const rangeConfig = thresholdRanges[field];

  let effectiveMin = min;
  let effectiveMax = max;
  let effectiveRange = max - min || 1;

  if (rangeConfig) {
    effectiveMin = Math.min(min, rangeConfig.min);
    effectiveMax = Math.max(max, rangeConfig.max);
    effectiveRange = effectiveMax - effectiveMin || 1;
  }

  const x = (i: number) => pad.left + (points.length > 1 ? (i / (points.length - 1)) * innerW : innerW / 2);
  const y = (v: number) => pad.top + innerH - ((v - effectiveMin) / effectiveRange) * innerH;

  const line = points.map((v, i) => `${i === 0 ? 'M' : 'L'} ${x(i)} ${y(v)}`).join(' ');
  const area = `${line} L ${x(points.length - 1)} ${pad.top + innerH} L ${x(0)} ${pad.top + innerH} Z`;

  const ticks = 5;
  const yTicks = Array.from({ length: ticks }, (_, i) => effectiveMin + (effectiveRange * i) / (ticks - 1));
  const xTicks = points.filter((_, i) => points.length <= 12 || i % Math.ceil(points.length / 12) === 0).map((_, i) => i);

  const colors = toneStyles[tone] || toneStyles.emerald;

  function clampY(value: number) {
    return Math.max(pad.top, Math.min(pad.top + innerH, value));
  }

  const alertY = rangeConfig ? clampY(pad.top + innerH - ((rangeConfig.alert - effectiveMin) / effectiveRange) * innerH) : null;
  const criticalY = rangeConfig ? clampY(pad.top + innerH - ((rangeConfig.critical - effectiveMin) / effectiveRange) * innerH) : null;

  return (
    <article className="glass-panel rounded-lg p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">{title}</h2>
          <p className="text-[11px] text-slate-500">
            {points.length} leitura{points.length !== 1 ? 's' : ''} • máx {fmt.format(max)}{suffix}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {rangeConfig && (
            <>
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-amber-400" />
                <span className="text-[10px] font-medium text-slate-400">Alerta {fmt.format(rangeConfig.alert)}{rangeConfig.unit}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-red-400" />
                <span className="text-[10px] font-medium text-slate-400">Crítico {fmt.format(rangeConfig.critical)}{rangeConfig.unit}</span>
              </span>
            </>
          )}
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ background: colors.stroke }} />
            <span className="text-[11px] font-medium text-slate-400">{field}</span>
          </span>
        </div>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="mt-4 h-56 w-full"
        role="img"
        aria-label={title}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <linearGradient id={`grad-${field}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={colors.fill} />
            <stop offset="100%" stopColor="rgba(0,0,0,0)" />
          </linearGradient>
        </defs>

        <rect x={pad.left} y={pad.top} width={innerW} height={innerH} fill="rgba(255,255,255,0.03)" rx="4" />

        {yTicks.map((v) => {
          const cy = y(v);
          return (
            <g key={v}>
              <line x1={pad.left} x2={pad.left + innerW} y1={cy} y2={cy} stroke="rgba(255,255,255,0.08)" strokeDasharray="4 4" />
              <text x={pad.left - 8} y={cy + 3} textAnchor="end" className="text-[10px] fill-slate-500">
                {fmt.format(v)}{suffix}
              </text>
            </g>
          );
        })}

        {criticalY !== null && (
          <line
            x1={pad.left}
            x2={pad.left + innerW}
            y1={criticalY}
            y2={criticalY}
            stroke="#ef4444"
            strokeDasharray="6 4"
            opacity="0.9"
          />
        )}
        {alertY !== null && (
          <line
            x1={pad.left}
            x2={pad.left + innerW}
            y1={alertY}
            y2={alertY}
            stroke="#f59e0b"
            strokeDasharray="6 4"
            opacity="0.9"
          />
        )}

        {xTicks.map((i) => {
          const cx = x(i);
          return (
            <text key={i} x={cx} y={pad.top + innerH + 18} textAnchor="middle" className="text-[10px] fill-slate-500">
              {i + 1}
            </text>
          );
        })}

        <path d={area} fill={`url(#grad-${field})`} opacity="0.7" />
        <path d={line} fill="none" stroke={colors.stroke} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

        {points.map((v, i) => (
          <circle key={i} cx={x(i)} cy={y(v)} r="3" fill={colors.stroke} stroke="rgba(0,0,0,0.4)" strokeWidth="1.5">
            <title>{`${fmt.format(v)}${suffix}`}</title>
          </circle>
        ))}
      </svg>
    </article>
  );
}

'use client';

import { useMemo } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  METRIC_META,
  STATUS_COLOR,
  STATUS_LABEL,
  buildPoints,
  formatAxis,
  formatLimit,
  formatMetric,
  summarize,
  type MetricStatus,
} from '@/lib/metrics';
import { METRIC_THRESHOLDS, visibleThresholds, type MetricKey } from '@/lib/metricThresholds';
import type { Telemetry } from '@/types/telemetry';

/* ──────────────────────────────────────────────────────────────────────────
   MetricColumnChart — o par de colunas do gráfico de linhas nos detalhes.

   Enquanto a linha responde "como a métrica evoluiu", as colunas respondem
   "quais leituras estavam fora da faixa": cada barra é pintada com a cor do
   status daquela leitura (esmeralda / âmbar / vermelho). Assim o mesmo dado é
   lido por dois ângulos complementares, sem repetir a mesma informação.
   ────────────────────────────────────────────────────────────────────────── */

type MetricColumnChartProps = {
  readings: Telemetry[];
  field: MetricKey;
  title: string;
  className?: string;
};

function ColumnTooltip({
  active,
  payload,
  unit,
  metric,
}: {
  active?: boolean;
  payload?: Array<{ payload?: { full: string; valor: number; status: MetricStatus } }>;
  unit: string;
  metric: MetricKey;
}) {
  const point = payload?.[0]?.payload;
  if (!active || !point) return null;

  return (
    <div className="liquid-glass--subtle min-w-36 rounded-xl px-3 py-2 text-[var(--text-1)] shadow-xl">
      <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
        {point.full}
      </p>
      <p className="mt-1 text-sm font-bold text-[var(--text-1)]">
        {/* Precisão da métrica — sem isso a vibração saía com três casas. */}
        {formatMetric(point.valor, metric)} {unit}
      </p>
      <p
        className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.08em]"
        style={{ color: STATUS_COLOR[point.status] }}
      >
        {STATUS_LABEL[point.status]}
      </p>
    </div>
  );
}

export function MetricColumnChart({
  readings,
  field,
  title,
  className = '',
}: MetricColumnChartProps) {
  const meta = METRIC_META[field];
  const config = METRIC_THRESHOLDS[field];

  const points = useMemo(() => buildPoints(readings, field), [readings, field]);
  const summary = useMemo(() => summarize(points), [points]);
  const { alert, critical } = useMemo(
    () => visibleThresholds(points.map((point) => point.valor), field),
    [points, field],
  );

  const domain = useMemo<[number, number]>(() => {
    if (!points.length) return [config.min, config.max];

    const values = points.map((point) => point.valor);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || Math.abs(max) * 0.2 || 1;

    let lo = min - span * 0.18;
    let hi = max + span * 0.18;
    for (const limit of [alert, critical]) {
      if (limit === null) continue;
      lo = Math.min(lo, limit);
      hi = Math.max(hi, limit);
    }
    lo = Math.max(lo, config.min);
    hi = Math.min(hi, config.max);
    if (hi <= lo) hi = lo + 1;
    return [lo, hi];
  }, [points, alert, critical, config]);

  return (
    <article
      className={`metric-card metric-chart-card metric-chart-card--${field} flex flex-col transition-all duration-200 ${className}`}
      aria-label={title}
    >
      <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h2 className="text-sm font-semibold text-[var(--text-2)]">{title}</h2>
          <p className="text-[11px] text-[var(--text-3)]">
            {summary.count} leitura{summary.count === 1 ? '' : 's'} ·{' '}
            {summary.foraDaFaixa === 0
              ? 'todas dentro da faixa'
              : `${summary.foraDaFaixa} fora da faixa`}
          </p>
        </div>
        <span className="shrink-0 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
          {meta.unit}
        </span>
      </div>

      <div className="mt-3 h-52 w-full">
        {points.length === 0 ? (
          <p className="flex h-full items-center justify-center text-xs text-[var(--text-3)]">
            Sem leituras no período.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={points} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 5" stroke="var(--chart-grid)" vertical={false} />

              <XAxis
                dataKey="label"
                tick={{ fill: 'var(--text-3)', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                minTickGap={18}
              />
              <YAxis
                domain={domain}
                tick={{ fill: 'var(--text-3)', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                width={56}
                tickFormatter={(value: number) => formatAxis(value, field)}
              />

              {alert !== null ? (
                <ReferenceLine
                  y={alert}
                  stroke="var(--status-atencao)"
                  strokeWidth={1.4}
                  strokeDasharray="7 5"
                  strokeOpacity={0.9}
                />
              ) : null}
              {critical !== null ? (
                <ReferenceLine
                  y={critical}
                  stroke="var(--status-critico)"
                  strokeWidth={1.4}
                  strokeDasharray="7 5"
                  strokeOpacity={0.9}
                />
              ) : null}

              <Tooltip
                cursor={{ fill: 'var(--chart-surface)', radius: 4 }}
                content={<ColumnTooltip unit={meta.unit} metric={field} />}
              />

              <Bar dataKey="valor" radius={[4, 4, 0, 0]} maxBarSize={28} isAnimationActive>
                {points.map((point, index) => (
                  <Cell key={`${point.label}-${index}`} fill={STATUS_COLOR[point.status]} fillOpacity={0.86} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <ul className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5" aria-label="Legenda do gráfico">
        {(['normal', 'atencao', 'critico'] as MetricStatus[]).map((status) => (
          <li
            key={status}
            className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]"
          >
            <span
              className="h-2 w-2 flex-shrink-0 rounded-sm"
              style={{ background: STATUS_COLOR[status] }}
              aria-hidden="true"
            />
            {STATUS_LABEL[status]}
          </li>
        ))}
        {alert !== null ? (
          <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
            <span className="threshold-rule threshold-rule--atencao" aria-hidden="true" />
            Limite {formatLimit(config.alert, field)}{meta.unit}
          </li>
        ) : null}
        {critical !== null ? (
          <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
            <span className="threshold-rule threshold-rule--critico" aria-hidden="true" />
            Risco {formatLimit(config.critical, field)}{meta.unit}
          </li>
        ) : null}
      </ul>

      <p className="mt-2 text-[10px] text-[var(--text-3)]">
        Média da janela: {formatMetric(summary.avg, field)}{meta.unit}
      </p>
    </article>
  );
}

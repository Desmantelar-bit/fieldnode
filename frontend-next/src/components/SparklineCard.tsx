'use client';

import {
  Area,
  AreaChart,
  ReferenceArea,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { METRIC_THRESHOLDS, type MetricKey } from '@/lib/metricThresholds';

type SparklineStatus = 'normal' | 'atencao' | 'critico';
type MetricKind = MetricKey;

const strokeHex: Record<SparklineStatus, string> = {
  normal:  'var(--chart-normal-stroke)',
  atencao: 'var(--chart-atencao-stroke)',
  critico: 'var(--chart-critico-stroke)',
};

const fillStop0: Record<SparklineStatus, string> = {
  normal:  'var(--chart-normal-stroke)',
  atencao: 'var(--chart-atencao-stroke)',
  critico: 'var(--chart-critico-stroke)',
};

const metricStroke: Record<MetricKind, string> = {
  temperatura: 'var(--metric-temperature)',
  vibracao: 'var(--metric-vibration)',
  rpm: 'var(--metric-rpm)',
};

/** Cor do texto do KPI: o que ele é, não de qual métrica ele é. */
const statusText: Record<SparklineStatus, string> = {
  normal:  'text-[color:var(--status-normal)]',
  atencao: 'text-[color:var(--status-atencao)]',
  critico: 'text-[color:var(--status-critico)]',
};

interface SparklineCardProps {
  titulo: string;
  valor: string | number;
  unidade?: string;
  dados: { valor: number; label?: string }[];
  status: SparklineStatus;
  metric?: MetricKind;
  tendencia?: string;
  /** Versão enxuta do KPI: número e sparkline menores, para o dashboard, onde
   *  o gráfico principal passou a carregar o destaque visual. */
  compact?: boolean;
}

function ChartTooltip({
  active,
  payload,
  label,
  unidade,
}: {
  active?: boolean;
  payload?: Array<{ value?: number }>;
  label?: string;
  unidade?: string;
}) {
  if (!active || !payload?.length) return null;
  const value = Number(payload[0]?.value);
  return (
    <div className="liquid-glass--subtle min-w-28 rounded-xl px-3 py-2 shadow-xl">
      <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">{label || 'Ponto'}</p>
      <p className="mt-1 text-sm font-bold text-[var(--text-1)]">{value.toLocaleString('pt-BR')}{unidade ? ` ${unidade}` : ''}</p>
    </div>
  );
}

export function SparklineCard({
  titulo,
  valor,
  unidade,
  dados,
  status,
  metric,
  tendencia,
  compact = false,
}: SparklineCardProps) {
  const stroke = metric ? metricStroke[metric] : strokeHex[status];
  // Valor sem leitura fica neutro; com leitura, segue o status (bom/alerta/risco).
  const valueTone = valor === '—' ? 'text-[var(--text-1)]' : statusText[status];
  const uid = `${status}-${titulo.replace(/\W/g, '')}`;
  const gradId = `area-${uid}`;
  const glowId = `glow-${uid}`;

  // Domínio dinâmico com margem de 12%
  const values = dados.map((d) => d.valor).filter(Number.isFinite);
  const minVal = values.length ? Math.min(...values) : 0;
  const maxVal = values.length ? Math.max(...values) : 1;
  const range = maxVal - minVal;
  const margin = range * 0.12 || Math.max(Math.abs(maxVal) * 0.1, 1);

  // Limites operacionais: fonte única (metricThresholds) e sempre visíveis.
  // As duas linhas pontilhadas — alerta (âmbar) e risco (vermelho) — aparecem
  // nas três métricas para comparar a leitura atual com o limite.
  const thresholds = metric ? METRIC_THRESHOLDS[metric] : null;
  const alertRef = thresholds?.alert ?? null;
  const criticalRef = thresholds?.critical ?? null;
  const refs = [alertRef, criticalRef].filter((value): value is number => value !== null);
  const domainMin = Math.min(minVal - margin, ...refs);
  const domainMax = Math.max(maxVal + margin, ...refs);
  const domain: [number, number] = [domainMin, domainMax];

  const normalBand = thresholds && alertRef !== null
    ? thresholds.higherIsWorse
      ? { from: domainMin, to: alertRef }
      : { from: alertRef, to: domainMax }
    : null;

  const lastDatum = dados.length ? dados[dados.length - 1] : null;
  const thresholdUnit = thresholds?.unit ?? unidade ?? '';
  const fmtLimit = (value: number) => new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(value);

  return (
    <article
      aria-label={titulo}
      className={`metric-card metric-card--status-${status} ${metric ? `metric-card--metric-${metric}` : `metric-card--${status}`} transition-all duration-200`}
    >
      <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
        {titulo}
      </p>

      <div className="mt-3 flex flex-col gap-1">
        <p
          className={`stat-value stat-value--${status} font-bold ${valueTone} ${
            compact ? 'text-3xl sm:text-4xl' : 'text-4xl sm:text-5xl'
          }`}
        >
          {valor}
          {unidade ? (
            <span className="ml-1 text-base font-normal text-[var(--text-3)] sm:text-lg">
              {unidade}
            </span>
          ) : null}
        </p>
        {tendencia ? <p className="text-xs text-[var(--text-3)]">{tendencia}</p> : null}
      </div>

      <div className={`w-full ${compact ? 'mt-3 h-12' : 'mt-4 h-16'}`} aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={dados} margin={{ top: 6, right: 4, left: 4, bottom: 0 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={fillStop0[status]} stopOpacity="0.56" />
                <stop offset="55%" stopColor={stroke} stopOpacity="0.18" />
                <stop offset="100%" stopColor="rgba(0,0,0,0)" />
              </linearGradient>
              <filter id={glowId} x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="3.5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            <XAxis dataKey="label" hide />
            <YAxis domain={domain} hide />

            {/* Faixa normal — mesmo idioma visual dos gráficos de detalhes */}
            {normalBand ? (
              <ReferenceArea
                y1={normalBand.from}
                y2={normalBand.to}
                fill="var(--status-normal)"
                fillOpacity={0.07}
                strokeOpacity={0}
              />
            ) : null}
            {alertRef !== null ? (
              <ReferenceLine
                y={alertRef}
                stroke="var(--status-atencao)"
                strokeWidth={1}
                strokeDasharray="3 4"
                strokeOpacity={0.5}
              />
            ) : null}
            {criticalRef !== null ? (
              <ReferenceLine
                y={criticalRef}
                stroke="var(--status-critico)"
                strokeWidth={1}
                strokeDasharray="3 4"
                strokeOpacity={0.5}
              />
            ) : null}

            <Tooltip
              cursor={{ stroke: stroke, strokeDasharray: '3 3', opacity: 0.35 }}
              content={<ChartTooltip unidade={unidade} />}
            />

            <Area
              type="monotone"
              dataKey="valor"
              stroke={stroke}
              strokeWidth={2}
              fill={`url(#${gradId})`}
              filter={`url(#${glowId})`}
              isAnimationActive
              animationDuration={700}
              animationEasing="ease-out"
              dot={false}
            />

            {/* Marcador da leitura atual — último ponto real da série */}
            {lastDatum && lastDatum.label ? (
              <ReferenceDot
                x={lastDatum.label}
                y={lastDatum.valor}
                r={3}
                fill={stroke}
                stroke="var(--background)"
                strokeWidth={1}
              />
            ) : null}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {alertRef !== null || criticalRef !== null ? (
        <ul className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1">
          <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
            <span className="threshold-band" aria-hidden="true" />
            Bom
          </li>
          {alertRef !== null ? (
            <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
              <span className="threshold-rule threshold-rule--atencao" aria-hidden="true" />
              Alerta {fmtLimit(alertRef)}{thresholdUnit}
            </li>
          ) : null}
          {criticalRef !== null ? (
            <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
              <span className="threshold-rule threshold-rule--critico" aria-hidden="true" />
              Risco {fmtLimit(criticalRef)}{thresholdUnit}
            </li>
          ) : null}
        </ul>
      ) : null}
    </article>
  );
}

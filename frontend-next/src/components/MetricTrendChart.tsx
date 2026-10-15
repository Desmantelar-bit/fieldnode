'use client';

import { useId, useMemo, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceArea,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  METRIC_META,
  METRIC_ORDER,
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
   MetricTrendChart — o gráfico principal da telemetria.

   Mostra UMA métrica por vez, escolhida pelas pílulas do cabeçalho. Uma série
   só (em vez de sobrepor RPM, temperatura e vibração) porque as três têm
   escalas muito diferentes — sobrepostas, as menores virariam linhas retas.
   Cada métrica em seu próprio eixo mantém a leitura honesta e o gráfico limpo.

   Sobre a janela: a API de telemetria devolve um número limitado de leituras
   recentes, então o rodapé informa explicitamente quantas estão no gráfico —
   nada de sugerir um histórico que não foi recebido.
   ────────────────────────────────────────────────────────────────────────── */

type MetricTrendChartProps = {
  readings: Telemetry[];
  /** Métrica aberta por padrão. */
  initialMetric?: MetricKey;
  className?: string;
};

function TrendTooltip({
  active,
  payload,
  unit,
  metric,
}: {
  active?: boolean;
  payload?: Array<{ payload?: { label: string; full: string; valor: number; status: MetricStatus } }>;
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
        {/* Precisão da métrica, e não o padrão do toLocaleString: vibração
            aparecia como "0,512 g" (três casas) no tooltip e "0,51 g" no card. */}
        {formatMetric(point.valor, metric)} {unit}
      </p>
      <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
        {STATUS_LABEL[point.status]}
      </p>
    </div>
  );
}

export function MetricTrendChart({
  readings,
  initialMetric = 'rpm',
  className = '',
}: MetricTrendChartProps) {
  const [metric, setMetric] = useState<MetricKey>(initialMetric);
  const uid = useId().replace(/[^a-zA-Z0-9]/g, '');
  const gradId = `trend-grad-${uid}`;
  const glowId = `trend-glow-${uid}`;

  const meta = METRIC_META[metric];
  const config = METRIC_THRESHOLDS[metric];

  const points = useMemo(() => buildPoints(readings, metric), [readings, metric]);
  const summary = useMemo(() => summarize(points), [points]);

  const { alert, critical } = useMemo(
    () => visibleThresholds(points.map((point) => point.valor), metric),
    [points, metric],
  );

  // Domínio legível: parte da variação real (não de 0→máximo) e só enquadra um
  // limite que esteja perto da série, para a curva não achatar.
  const domain = useMemo<[number, number]>(() => {
    if (!points.length) return [config.min, config.max];

    const values = points.map((point) => point.valor);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || Math.abs(max) * 0.2 || 1;

    let lo = min - span * 0.15;
    let hi = max + span * 0.15;
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

  // Faixa "boa": o lado oposto ao risco.
  const normalBand = alert !== null
    ? config.higherIsWorse
      ? { from: domain[0], to: alert }
      : { from: alert, to: domain[1] }
    : null;

  const lastPoint = points.length ? points[points.length - 1] : null;
  const currentStatus: MetricStatus = lastPoint ? lastPoint.status : 'normal';

  return (
    <section
      aria-label={`Gráfico de ${meta.label}`}
      className={`metric-card flex flex-col transition-all duration-200 ${className}`}
    >
      {/* ── Cabeçalho: título + troca de métrica ── */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]">
            Telemetria da máquina
          </p>
          <h2 className="mt-0.5 text-sm font-semibold text-[var(--text-1)]">
            {meta.label}
          </h2>
        </div>

        <div
          role="tablist"
          aria-label="Escolher métrica do gráfico"
          className="flex shrink-0 flex-wrap gap-1.5"
        >
          {METRIC_ORDER.map((key) => {
            const active = key === metric;
            return (
              <button
                key={key}
                type="button"
                role="tab"
                aria-selected={active}
                onClick={() => setMetric(key)}
                className={`rounded-full px-3 py-1.5 text-[11px] font-semibold transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
                  active
                    ? 'text-[color:var(--brand-on-accent)]'
                    : 'text-[var(--text-3)] hover:text-[var(--text-1)]'
                }`}
                style={
                  active
                    ? { backgroundImage: 'var(--brand-gradient)' }
                    : { background: 'var(--panel-glass-mid)' }
                }
              >
                {METRIC_META[key].short}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Valor atual + resumo da janela ──
          Centralizado: o número grande é o valor da LEITURA, e os quatro
          números ao lado são estatística da JANELA. Antes, o bloco encostava à
          esquerda e os secundários saíam desalinhados entre si (larguras
          diferentes por causa do rótulo "Fora da faixa"). Cada estatística
          ganhou largura mínima e alinhamento próprio, então a linha fica numa
          grade legível mesmo quando os valores mudam de tamanho. */}
      <div className="mt-5 flex flex-col items-center gap-4 text-center">
        <div className="min-w-0">
          <p
            className="stat-value text-4xl font-bold sm:text-5xl"
            style={{ color: lastPoint ? 'var(--text-1)' : 'var(--text-3)' }}
          >
            {lastPoint ? formatMetric(lastPoint.valor, metric) : '—'}
            {lastPoint ? (
              <span className="ml-1.5 text-base font-normal text-[var(--text-3)] sm:text-lg">
                {meta.unit}
              </span>
            ) : null}
          </p>
          <p className="mt-1 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
            Leitura mais recente ·{' '}
            <span style={{ color: `var(--status-${currentStatus})` }}>
              {STATUS_LABEL[currentStatus]}
            </span>
          </p>
        </div>

        <dl className="flex w-full flex-wrap items-start justify-center gap-x-2 gap-y-2 sm:gap-x-6">
          {[
            { term: 'Mínima', value: formatMetric(summary.min, metric) },
            { term: 'Média', value: formatMetric(summary.avg, metric) },
            { term: 'Máxima', value: formatMetric(summary.max, metric) },
            { term: 'Fora da faixa', value: String(summary.foraDaFaixa) },
          ].map(({ term, value }) => (
            <div key={term} className="flex flex-col items-center" style={{ minWidth: '4.5rem' }}>
              <dt className="text-[9px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)] text-center whitespace-nowrap">
                {term}
              </dt>
              <dd className="mt-0.5 text-[15px] font-semibold tabular-nums text-[var(--text-2)] text-center">
                {value}
              </dd>
            </div>
          ))}
        </dl>
      </div>

      {/* ── Gráfico ──
          A `key` na métrica REMONTA a área quando o usuário troca de série, e
          com isso o Recharts repete a animação de traçado — é a animaçãozinha
          que existia antes ao trocar de gráfico. Sem a key, o Recharts apenas
          substitui os dados e a curva salta de um desenho para o outro. */}
      <div key={`chart-${metric}`} className="chart-swap mt-4 h-56 w-full sm:h-72">
        {points.length === 0 ? (
          <p className="flex h-full items-center justify-center text-xs text-[var(--text-3)]">
            Sem leituras disponíveis para esta máquina.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart key={`area-${metric}`} data={points} margin={{ top: 8, right: 10, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={meta.color} stopOpacity={0.42} />
                  <stop offset="60%" stopColor={meta.color} stopOpacity={0.12} />
                  <stop offset="100%" stopColor="var(--chart-transparent)" />
                </linearGradient>
                <filter id={glowId} x="-30%" y="-30%" width="160%" height="160%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              <CartesianGrid strokeDasharray="3 5" stroke="var(--chart-grid)" vertical={false} />

              <XAxis
                dataKey="label"
                tick={{ fill: 'var(--text-3)', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                minTickGap={24}
              />
              <YAxis
                domain={domain}
                tick={{ fill: 'var(--text-3)', fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                /* RPM: "2.444" = 5 chars com separador de milhar → 64px.
                   Temperatura: "110,0 °C" → 64px também.
                   Vibração: "0,80 g" → 52px. Usamos 64 fixo para os três não
                   ficarem com larguras diferentes ao trocar de métrica. */
                width={64}
                tickFormatter={(value: number) => formatAxis(value, metric)}
              />

              {/* Faixa operacional boa */}
              {normalBand ? (
                <ReferenceArea
                  y1={normalBand.from}
                  y2={normalBand.to}
                  fill="var(--status-normal)"
                  fillOpacity={0.08}
                  strokeOpacity={0}
                />
              ) : null}

              {/* Limites: âmbar = atenção, vermelho = risco */}
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
                cursor={{ stroke: meta.color, strokeDasharray: '3 3', opacity: 0.4 }}
                content={<TrendTooltip unit={meta.unit} metric={metric} />}
              />

              <Area
                type="monotone"
                dataKey="valor"
                stroke={meta.color}
                strokeWidth={2.4}
                fill={`url(#${gradId})`}
                filter={`url(#${glowId})`}
                dot={false}
                activeDot={{ r: 4, stroke: 'var(--background)', strokeWidth: 1.5 }}
                animationDuration={700}
                animationEasing="ease-out"
              />

              {lastPoint ? (
                <ReferenceDot
                  x={lastPoint.label}
                  y={lastPoint.valor}
                  r={4}
                  fill={meta.color}
                  stroke="var(--background)"
                  strokeWidth={1.5}
                />
              ) : null}
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* ── Legenda + janela real dos dados ── */}
      <div className="mt-3 flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <ul className="flex flex-wrap items-center gap-x-4 gap-y-1.5" aria-label="Legenda do gráfico">
          <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
            <span className="h-2 w-2 rounded-full" style={{ background: meta.color }} aria-hidden="true" />
            {meta.short}
          </li>
          <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
            <span className="threshold-band" aria-hidden="true" />
            Faixa boa
          </li>
          {alert !== null ? (
            <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
              <span className="threshold-rule threshold-rule--atencao" aria-hidden="true" />
              Atenção {formatLimit(config.alert, metric)}{meta.unit}
            </li>
          ) : null}
          {critical !== null ? (
            <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
              <span className="threshold-rule threshold-rule--critico" aria-hidden="true" />
              Risco {formatLimit(config.critical, metric)}{meta.unit}
            </li>
          ) : null}
        </ul>

        <p className="text-[10px] text-[var(--text-3)]">
          {summary.count} leitura{summary.count === 1 ? '' : 's'} mais recente
          {summary.count === 1 ? '' : 's'} recebida{summary.count === 1 ? '' : 's'} da API
        </p>
      </div>
    </section>
  );
}

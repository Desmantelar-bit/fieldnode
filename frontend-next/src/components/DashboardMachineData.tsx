'use client';

import { useEffect, useMemo, useState } from 'react';
import { ChevronDown, LoaderCircle } from 'lucide-react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { MetricTrendChart } from '@/components/MetricTrendChart';
import { SparklineCard } from '@/components/SparklineCard';
import { telemetryService } from '@/services/telemetryService';
import {
  METRIC_META,
  METRIC_ORDER,
  buildPoints,
  statusOf,
  summarize,
  type MetricStatus,
} from '@/lib/metrics';
import type { Machine, Telemetry } from '@/types/telemetry';
import { mockRpmSeries, mockTemperaturaSeries, mockVibracaoSeries } from '@/data/mockData';

/* ──────────────────────────────────────────────────────────────────────────
   DashboardMachineData — o bloco de telemetria do dashboard.

   Estrutura: seletor de máquina → gráfico principal de tendência → KPIs
   compactos com mini-sparkline → distribuição operacional por faixa.

   A regra de leitura (série, média e classificação por status) NÃO mora mais
   aqui: veio de `@/lib/metrics`, para os três gráficos do app usarem a mesma
   classificação e não existirem duas verdades sobre "o que é uma leitura boa".
   ────────────────────────────────────────────────────────────────────────── */

const DEMO_SERIES: Record<string, { valor: number; label: string }[]> = {
  rpm: mockRpmSeries,
  temperatura: mockTemperaturaSeries,
  vibracao: mockVibracaoSeries,
};

/** Constrói série temporal de "score operacional" para o AreaChart.
 *  Cada ponto = uma leitura. O valor é 0 (crítico), 50 (atenção) ou 100 (normal),
 *  tornando visível a evolução do estado da máquina no tempo — é exatamente o que
 *  o AreaChart estilo MetricTrendChart comunica melhor que barras empilhadas. */
function buildHealthSeries(readings: Telemetry[]) {
  return [...readings]
    .reverse()
    .flatMap((r) => {
      const points = METRIC_ORDER.map((m) => buildPoints([r], m)[0]).filter(Boolean);
      if (!points.length) return [];
      // Score: mínimo dos três status neste timestamp
      const scores = points.map((p) => (p.status === 'normal' ? 100 : p.status === 'atencao' ? 50 : 0));
      const score = Math.min(...scores);
      const raw = r.timestamp ? new Date(r.timestamp) : null;
      const valid = raw !== null && !Number.isNaN(raw.getTime());
      return [{
        label: valid ? raw.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '',
        full: valid ? raw.toLocaleString('pt-BR') : 'sem data',
        score,
        status: score === 100 ? 'normal' : score === 50 ? 'atencao' : 'critico',
      }];
    });
}

/** As três faixas, mantido para compatibilidade com buildOperationalBands abaixo. */
const BAND_SERIES = [
  { key: 'normal', label: 'Normal', color: 'var(--chart-normal-stroke)' },
  { key: 'atencao', label: 'Atenção', color: 'var(--chart-atencao-stroke)' },
  { key: 'critico', label: 'Crítico', color: 'var(--chart-critico-stroke)' },
] as const;

/** Mantido para o tooltip de contagens */
function buildOperationalBands(readings: Telemetry[]) {
  return METRIC_ORDER.map((metric) => {
    const counts = { metrica: METRIC_META[metric].short, normal: 0, atencao: 0, critico: 0 };
    for (const point of buildPoints(readings, metric)) counts[point.status] += 1;
    return counts;
  });
}

type HealthPoint = { label: string; full: string; score: number; status: string };

function HealthTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload?: HealthPoint }>;
}) {
  const pt = payload?.[0]?.payload;
  if (!active || !pt) return null;
  const color =
    pt.status === 'normal' ? 'var(--status-normal)'
    : pt.status === 'atencao' ? 'var(--status-atencao)'
    : 'var(--status-critico)';
  const label =
    pt.status === 'normal' ? 'Normal'
    : pt.status === 'atencao' ? 'Atenção'
    : 'Crítico';
  return (
    <div className="liquid-glass--subtle min-w-32 rounded-xl px-3 py-2 text-[var(--text-1)]">
      <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">{pt.full}</p>
      <p className="mt-1 text-sm font-bold" style={{ color }}>{label}</p>
      <p className="text-[10px] text-[var(--text-3)]">score {pt.score}/100</p>
    </div>
  );
}

/** Gráfico de saúde operacional — AreaChart no estilo do MetricTrendChart.
 *  Mostra a evolução do estado da máquina no tempo (normal → atenção → crítico)
 *  como uma área suavizada, com glow na linha e zona de risco destacada. */
function OperationalHealthChart({ readings }: { readings: Telemetry[] }) {
  const series = useMemo(() => buildHealthSeries(readings), [readings]);
  const bands = useMemo(() => buildOperationalBands(readings), [readings]);
  const total = bands.reduce((s, b) => s + b.normal + b.atencao + b.critico, 0);
  const foraDaFaixa = bands.reduce((s, b) => s + b.atencao + b.critico, 0);

  // Cor da linha acompanha o último status
  const lastPt = series[series.length - 1];
  const currentStatus = lastPt?.status ?? 'normal';
  const lineColor =
    currentStatus === 'normal' ? 'var(--status-normal)'
    : currentStatus === 'atencao' ? 'var(--status-atencao)'
    : 'var(--status-critico)';

  const gradId = 'health-grad';
  const glowId = 'health-glow';

  return (
    <section
      aria-label="Saúde operacional ao longo do tempo"
      className="metric-card flex flex-col"
      style={{ minHeight: '100%' }}
    >
      {/* Cabeçalho */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]">
            Saúde operacional
          </p>
          <h2 className="mt-0.5 text-sm font-semibold text-[var(--text-1)]">
            Evolução no tempo
          </h2>
        </div>
        {total > 0 && (
          <p className="shrink-0 text-right text-[11px] text-[var(--text-3)]">
            {total} leituras · {foraDaFaixa > 0
              ? <span style={{ color: 'var(--status-atencao)' }}>{foraDaFaixa} fora</span>
              : 'todas normais'}
          </p>
        )}
      </div>

      {/* Valor atual */}
      {lastPt ? (
        <div className="mt-3 flex items-baseline gap-2">
          <p
            className="stat-value text-3xl font-bold"
            style={{ color: lineColor }}
          >
            {lastPt.score}
            <span className="ml-1 text-base font-normal text-[var(--text-3)]">/100</span>
          </p>
          <p className="text-[11px] font-semibold uppercase tracking-[0.08em]" style={{ color: lineColor }}>
            {currentStatus === 'normal' ? 'Normal' : currentStatus === 'atencao' ? 'Atenção' : 'Crítico'}
          </p>
        </div>
      ) : null}

      {/* Área */}
      {series.length === 0 ? (
        <p className="flex flex-1 items-center justify-center py-8 text-xs text-[var(--text-3)]">
          Sem leituras disponíveis para esta máquina.
        </p>
      ) : (
        <div key={`health-${readings.length}`} className="chart-swap mt-3 flex-1" style={{ minHeight: '140px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={series} margin={{ top: 6, right: 6, left: -24, bottom: 0 }}>
              <defs>
                <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={lineColor} stopOpacity={0.40} />
                  <stop offset="60%" stopColor={lineColor} stopOpacity={0.10} />
                  <stop offset="100%" stopColor="transparent" />
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
                minTickGap={28}
              />
              <YAxis
                domain={[0, 100]}
                ticks={[0, 50, 100]}
                tick={{ fill: 'var(--text-3)', fontSize: 9 }}
                axisLine={false}
                tickLine={false}
                width={36}
              />
              <Tooltip content={<HealthTooltip />} cursor={{ stroke: lineColor, strokeDasharray: '3 3', opacity: 0.35 }} />
              <Area
                type="monotone"
                dataKey="score"
                stroke={lineColor}
                strokeWidth={2.2}
                fill={`url(#${gradId})`}
                filter={`url(#${glowId})`}
                dot={false}
                activeDot={{ r: 4, stroke: 'var(--background)', strokeWidth: 1.5 }}
                animationDuration={700}
                animationEasing="ease-out"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Legenda de contagens */}
      {total > 0 && (
        <ul className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5">
          {BAND_SERIES.map(({ key, label, color }) => {
            const qty = bands.reduce((s, b) => s + b[key], 0);
            return (
              <li key={key} className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
                <span className="h-2 w-2 shrink-0 rounded-sm" style={{ background: color }} aria-hidden="true" />
                {label}
                <span className="tabular-nums text-[var(--text-2)]">{qty}</span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

/** Card compacto de horário da operação — clean, sem o mostrador SVG grande. */
function OperationTimeCard() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const id = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const hora = now
    ? now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    : '--:--';
  const segundos = now ? now.toLocaleTimeString('pt-BR', { second: '2-digit' }) : '--';
  const data = now
    ? now.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: 'short' })
    : '';

  return (
    <section
      aria-label="Horário da operação"
      className="metric-card flex flex-col items-center justify-center gap-2 text-center"
      style={{ minHeight: '100%' }}
    >
      <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]">
        Operação agora
      </p>

      {/* Hora grande */}
      <p className="stat-value mt-1 text-5xl font-bold tracking-tight text-[var(--text-1)] sm:text-6xl">
        {hora}
      </p>
      <p className="text-sm text-[var(--text-3)] tabular-nums">:{segundos}</p>

      {/* Data */}
      {now ? (
        <time dateTime={now.toISOString()} className="mt-1 text-[11px] capitalize text-[var(--text-3)]">
          {data}
        </time>
      ) : (
        <p className="mt-1 text-[11px] text-[var(--text-3)]">—</p>
      )}
    </section>
  );
}

export function DashboardMachineData({
  machines,
  initialReadings,
}: {
  machines: Machine[];
  initialReadings: Telemetry[];
}) {
  const options = machines.filter((machine) => Boolean(machine.maquina_id));
  const [selectedMachineId, setSelectedMachineId] = useState(options[0]?.maquina_id ?? '');
  const [readings, setReadings] = useState(() =>
    initialReadings.filter((reading) => reading.maquina_id === options[0]?.maquina_id),
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedMachineId) {
      setReadings([]);
      return;
    }

    // A leitura mais recente já chega pronta do servidor e entra como estado
    // imediato, para o número aparecer sem espera. A JANELA COMPLETA vem em
    // seguida porque o gráfico de tendência precisa da série inteira — com uma
    // leitura só ele viraria um ponto solto num eixo vazio.
    const initial = initialReadings.filter((reading) => reading.maquina_id === selectedMachineId);
    setReadings(initial);

    let cancelled = false;
    setLoading(true);
    setError(null);

    telemetryService
      .getMachineReadings(selectedMachineId)
      .then((data) => {
        if (!cancelled && data.length) setReadings(data);
      })
      .catch((err: unknown) => {
        // Só reporta falha se não houver nada para mostrar — se a leitura
        // recente já veio no SSR, o painel continua útil.
        if (!cancelled && initial.length === 0) {
          setError(err instanceof Error ? err.message : 'Falha ao carregar a máquina.');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [initialReadings, selectedMachineId]);

  const machine = options.find((item) => item.maquina_id === selectedMachineId);
  const hasReadings = readings.length > 0;

  /** Um KPI por métrica, já com série ordenada, média e status resolvidos. */
  const kpis = useMemo(
    () =>
      METRIC_ORDER.map((metric) => {
        const points = buildPoints(readings, metric);
        const summary = summarize(points);
        const meta = METRIC_META[metric];
        const demo = !hasReadings;
        const dados = demo ? DEMO_SERIES[metric] : points.map((point) => ({ valor: point.valor, label: point.label }));
        const valor = demo ? summary.avg : summary.avg;
        const status: MetricStatus = statusOf(valor, metric);

        return { metric, meta, dados, valor, status, demo };
      }),
    [readings, hasReadings],
  );

  return (
    <section aria-label="Indicadores da máquina selecionada" className="space-y-4">
      {/* Seletor de máquina */}
      <div className="fleet-summary flex flex-col gap-3 rounded-2xl p-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <div>
            <p className="section-heading">Máquina selecionada</p>
            <p className="text-sm font-semibold text-[var(--text-1)]">
              {machine?.maquina_id ?? 'Nenhuma máquina disponível'}
            </p>
          </div>
          {loading ? (
            <LoaderCircle
              size={15}
              className="animate-spin text-[color:var(--ui-accent)]"
              aria-label="Atualizando dados"
            />
          ) : null}
        </div>
        <label className="relative w-full sm:w-72">
          <span className="sr-only">Selecionar máquina</span>
          <select
            value={selectedMachineId}
            onChange={(event) => setSelectedMachineId(event.target.value)}
            className="data-tile h-11 w-full appearance-none border px-3 pr-9 text-sm font-medium text-[var(--text-1)] outline-none focus:border-[color:var(--ui-accent)] focus:ring-2 focus:ring-[color:var(--ui-accent)]/20"
          >
            {options.map((item) => (
              <option key={item.maquina_id} value={item.maquina_id}>
                {item.maquina_id} · {item.modelo.nome}
              </option>
            ))}
          </select>
          <ChevronDown
            size={14}
            className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-2)]"
            aria-hidden="true"
          />
        </label>
      </div>

      {error ? (
        <p className="rounded-xl border border-[color:var(--status-critico)]/30 bg-[color:var(--status-critico)]/10 p-3 text-xs text-[var(--text-2)]">
          {error}
        </p>
      ) : null}

      {/* Gráfico principal de telemetria */}
      <MetricTrendChart key={`trend-${selectedMachineId}`} readings={readings} initialMetric="rpm" />

      {/* Médias por métrica — um painel só, com três colunas divididas por fios.
          O título "Valores médios" existe porque os três números são MÉDIAS do
          período: sem ele, "1839 rpm" é lido como a leitura atual, o que confunde
          quem acabou de ver 1.627 rpm no gráfico acima. */}
      <section aria-label="Valores médios por métrica" className="kpi-group">
        <div className="kpi-group__head">
          <div>
            <p className="kpi-group__title">Valores médios</p>
            <p className="kpi-group__sub">
              {hasReadings
                ? `Média de ${readings.length} leituras de ${machine?.maquina_id ?? '—'}`
                : 'Sem leitura registrada — série demonstrativa'}
            </p>
          </div>
          {kpis.some((kpi) => kpi.demo) ? (
            <span className="kpi-group__badge">demonstrativo</span>
          ) : null}
        </div>

        <div className="kpi-group__grid">
          {kpis.map(({ metric, meta, dados, valor, status, demo }) => (
            <SparklineCard
              key={`${selectedMachineId}-${metric}`}
              titulo={meta.label}
              valor={demo ? valor : (meta.digits === 0 ? Math.round(valor) : valor.toFixed(meta.digits))}
              unidade={meta.unit}
              dados={dados}
              status={status}
              metric={metric}
              compact
            />
          ))}
        </div>
      </section>

      {/* Saúde operacional (AreaChart) + horário clean, lado a lado. */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)] lg:items-stretch">
        <OperationalHealthChart readings={readings} />
        <OperationTimeCard />
      </div>
    </section>
  );
}

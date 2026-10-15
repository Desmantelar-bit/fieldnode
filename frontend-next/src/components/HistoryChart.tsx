import { useEffect, useRef, useState } from 'react';
import type { Telemetry } from '@/types/telemetry';
import { chartColors } from '@/lib/theme';
import { METRIC_THRESHOLDS } from '@/lib/metricThresholds';

type ChartTone = 'red' | 'amber' | 'emerald';

const metricStyles = {
  temperatura: { stroke: 'var(--metric-temperature)', label: 'Temperatura' },
  vibracao: { stroke: 'var(--metric-vibration)', label: 'Vibração' },
  rpm: { stroke: 'var(--metric-rpm)', label: 'RPM' },
} as const;

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
  tone: ChartTone;
}) {
  const points = readings.map((r) => Number(r[field])).reverse();
  const pointLabels = readings.map((reading) => new Date(reading.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })).reverse();
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  // O SVG é desenhado 1:1 em pixels: assim rótulos, pontos e linhas ficam no
  // tamanho real da tela (com o viewBox fixo de 640px tudo encolhia no card).
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [measuredW, setMeasuredW] = useState(0);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const update = () => setMeasuredW(Math.round(el.clientWidth));
    update();
    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', update);
      return () => window.removeEventListener('resize', update);
    }
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  if (!points.length) {
    return (
      <article className="metric-card">
        <h2 className="text-sm font-semibold text-[var(--text-2)]">{title}</h2>
        <p className="mt-4 text-xs text-[var(--text-3)]">Sem leituras no período.</p>
      </article>
    );
  }

  const width  = measuredW || 640;
  const height = width < 420 ? 220 : 264;
  const narrow = width < 420;
  const pad    = { top: 18, right: narrow ? 46 : 60, bottom: 30, left: narrow ? 44 : 52 };
  const innerW = Math.max(width - pad.left - pad.right, 40);
  const innerH = height - pad.top - pad.bottom;

  const max = Math.max(...points);
  const min = Math.min(...points);
  const mean = points.reduce((acc, v) => acc + v, 0) / points.length;
  const rangeConfig = METRIC_THRESHOLDS[field];

  // Domínio legível: parte da variação real (e não do 0→máximo absoluto, que
  // achatava a curva) e só entra no enquadramento um limite que estiver perto.
  // Cálculo direto (sem useMemo) porque fica depois do retorno de "sem leituras".
  const domain = (() => {
    const span = max - min || Math.abs(max) * 0.2 || 1;
    const margin = span * 0.18;
    let lo = min - margin;
    let hi = max + margin;
    for (const t of [rangeConfig?.alert, rangeConfig?.critical]) {
      if (t === undefined) continue;
      if (t >= lo - span * 0.6 && t <= hi + span * 0.6) {
        lo = Math.min(lo, t);
        hi = Math.max(hi, t);
      }
    }
    if (rangeConfig) {
      lo = Math.max(lo, rangeConfig.min);
      hi = Math.min(hi, rangeConfig.max);
    }
    if (hi <= lo) hi = lo + 1;
    return { lo, hi, span: hi - lo };
  })();

  const x = (i: number) => pad.left + (points.length > 1 ? (i / (points.length - 1)) * innerW : innerW / 2);
  const y = (v: number) => pad.top + innerH - ((v - domain.lo) / domain.span) * innerH;

  const line = points.map((v, i) => `${i === 0 ? 'M' : 'L'} ${x(i)} ${y(v)}`).join(' ');
  const area = `${line} L ${x(points.length - 1)} ${pad.top + innerH} L ${x(0)} ${pad.top + innerH} Z`;

  const ticks  = 4;
  const yTicks = Array.from({ length: ticks + 1 }, (_, i) => domain.lo + (domain.span * i) / ticks);
  const xTicks = points
    .map((_, i) => i)
    .filter((i) => points.length <= 6 || i % Math.ceil(points.length / 6) === 0);

  const metric = metricStyles[field];

  const inRange = (v: number) => v >= domain.lo && v <= domain.hi;
  const alertY    = rangeConfig && inRange(rangeConfig.alert)    ? y(rangeConfig.alert)    : null;
  const criticalY = rangeConfig && inRange(rangeConfig.critical) ? y(rangeConfig.critical) : null;

  // Faixa operacional boa: o lado oposto ao risco.
  const bandFrom = rangeConfig && rangeConfig.higherIsWorse
    ? domain.lo
    : Math.max(rangeConfig ? rangeConfig.alert : domain.lo, domain.lo);
  const bandTo = rangeConfig && rangeConfig.higherIsWorse
    ? Math.min(Math.max(rangeConfig.alert, domain.lo), domain.hi)
    : domain.hi;

  const showDots = points.length <= 60;
  const lastIndex = points.length - 1;
  const minIndex = points.indexOf(min);
  const maxIndex = points.indexOf(max);
  const tickAnchor = (i: number) => (i === 0 ? 'start' : i === lastIndex ? 'end' : 'middle');

  return (
    <article
      className={`metric-card metric-chart-card metric-chart-card--${field} transition-all duration-200`}
      data-risk-tone={tone}
      onClick={() => setSelectedIndex(null)}
    >
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h2 className="text-sm font-semibold text-[var(--text-2)]">{title}</h2>
          <p className="text-[11px] text-[var(--text-3)]">
            {points.length} leitura{points.length !== 1 ? 's' : ''} · mín {fmt.format(min)}{suffix} · máx {fmt.format(max)}{suffix} · média {fmt.format(mean)}{suffix}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full" style={{ background: metric.stroke }} />
            <span className="text-[10px] font-semibold text-[var(--text-2)]">{metric.label}</span>
          </span>
        </div>
      </div>

      <div ref={wrapRef} className="mt-3 w-full">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        style={{ height }}
        role="img"
        aria-label={`${title}: ${points.length} leituras, mínima ${fmt.format(min)}${suffix}, máxima ${fmt.format(max)}${suffix}, média ${fmt.format(mean)}${suffix}`}
        preserveAspectRatio="xMidYMid meet"
        onClick={() => setSelectedIndex(null)}
      >
        <defs>
          <linearGradient id={`grad-${field}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%"   stopColor={metric.stroke} stopOpacity="0.28" />
            <stop offset="100%" stopColor={chartColors.transparent} />
          </linearGradient>
          <filter id={`glow-${field}`} x="-25%" y="-25%" width="150%" height="150%">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect x={pad.left} y={pad.top} width={innerW} height={innerH} fill={chartColors.surface} rx="8" />

        {/* Faixa "boa": mostra de imediato onde a leitura está saudável. */}
        <rect
          x={pad.left}
          y={Math.max(Math.min(y(bandTo), y(bandFrom)), pad.top)}
          width={innerW}
          height={Math.abs(y(bandFrom) - y(bandTo))}
          fill="var(--status-normal)"
          fillOpacity="0.10"
          rx="6"
        />

        {yTicks.map((v) => {
          const cy = y(v);
          return (
            <g key={v}>
              <line x1={pad.left} x2={pad.left + innerW} y1={cy} y2={cy} stroke={chartColors.grid} strokeDasharray="3 5" />
              <text x={pad.left - 8} y={cy + 3.5} textAnchor="end" fill="var(--text-3)" fontSize="10">
                {fmt.format(v)}
              </text>
            </g>
          );
        })}

        {/* Limites operacionais, com o valor escrito na própria linha. */}
        {criticalY !== null && (
          <g>
            <line x1={pad.left} x2={pad.left + innerW} y1={criticalY} y2={criticalY}
              stroke={chartColors.critico.stroke} strokeWidth="1.4" strokeDasharray="7 5" opacity="0.95" />
            <text x={pad.left + innerW + 6} y={criticalY + 3.5} textAnchor="start" fill={chartColors.critico.stroke} fontSize="10" fontWeight="700">
              {fmt.format(rangeConfig.critical)}
            </text>
          </g>
        )}
        {alertY !== null && (
          <g>
            <line x1={pad.left} x2={pad.left + innerW} y1={alertY} y2={alertY}
              stroke={chartColors.atencao.stroke} strokeWidth="1.4" strokeDasharray="7 5" opacity="0.95" />
            <text x={pad.left + innerW + 6} y={alertY + 3.5} textAnchor="start" fill={chartColors.atencao.stroke} fontSize="10" fontWeight="700">
              {fmt.format(rangeConfig.alert)}
            </text>
          </g>
        )}

        {/* Média: referência rápida para saber se a série sobe ou desce. */}
        <line x1={pad.left} x2={pad.left + innerW} y1={y(mean)} y2={y(mean)}
          stroke="var(--text-3)" strokeWidth="1" strokeDasharray="2 4" opacity="0.55" />

        {xTicks.map((i) => (
          <text key={i} x={x(i)} y={pad.top + innerH + 16} textAnchor={tickAnchor(i)} fill="var(--text-3)" fontSize="10">
            {pointLabels[i] ?? i + 1}
          </text>
        ))}

        <path d={area} fill={`url(#grad-${field})`} opacity="0.45" />
        <path d={line} fill="none" stroke={metric.stroke} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" filter={`url(#glow-${field})`} />

        {/* Cada leitura vira um ponto clicável quando a série é curta o bastante. */}
        {showDots
          ? points.map((v, i) => {
              if (i === lastIndex || i === minIndex || i === maxIndex) return null;
              return (
                <circle
                  key={i}
                  cx={x(i)}
                  cy={y(v)}
                  r={selectedIndex === i ? 5 : 2.4}
                  className="cursor-pointer"
                  fill={metric.stroke}
                  opacity={selectedIndex === i ? 1 : 0.55}
                  onClick={(event) => {
                    event.stopPropagation();
                    setSelectedIndex((current) => current === i ? null : i);
                  }}
                >
                  <title>{`${fmt.format(v)}${suffix} · ${pointLabels[i] ?? ''}`}</title>
                </circle>
              );
            })
          : null}

        {/* Mínima, máxima e leitura atual (a mais recente). */}
        {[minIndex, maxIndex, lastIndex]
          .filter((i, idx, arr) => arr.indexOf(i) === idx)
          .map((i) => (
            <circle
              key={`marker-${i}`}
              cx={x(i)}
              cy={y(points[i])}
              r={i === lastIndex ? 5 : 3.6}
              fill={i === lastIndex ? metric.stroke : 'var(--panel)'}
              stroke={metric.stroke}
              strokeWidth="2"
              opacity={selectedIndex === i ? 1 : 0.95}
            >
              <title>{`${fmt.format(points[i])}${suffix} · ${pointLabels[i] ?? ''}`}</title>
            </circle>
          ))}

        {selectedIndex !== null && points[selectedIndex] !== undefined ? (
          <g pointerEvents="none" transform={`translate(${Math.min(Math.max(x(selectedIndex) - 58, 4), width - 120)}, ${Math.max(y(points[selectedIndex]) - 48, 4)})`}>
            <rect width="116" height="36" rx="8" fill="var(--panel)" stroke="var(--line)" />
            <text x="58" y="14" textAnchor="middle" fill="var(--text-3)" fontSize="9">{pointLabels[selectedIndex] ?? 'Ponto'}</text>
            <text x="58" y="28" textAnchor="middle" fill="var(--text-1)" fontSize="11" fontWeight="700">{fmt.format(points[selectedIndex])}{suffix}</text>
          </g>
        ) : null}
      </svg>
      </div>

      {/* Legenda: mesmo vocabulário visual da mini-sparkline dos KPIs. */}
      <ul className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5">
        <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
          <span className="threshold-band" aria-hidden="true" />
          Faixa boa
        </li>
        {alertY !== null && (
          <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
            <span className="threshold-rule threshold-rule--atencao" aria-hidden="true" />
            Atenção {fmt.format(rangeConfig.alert)}{suffix}
          </li>
        )}
        {criticalY !== null && (
          <li className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
            <span className="threshold-rule threshold-rule--critico" aria-hidden="true" />
            Crítico {fmt.format(rangeConfig.critical)}{suffix}
          </li>
        )}
      </ul>
    </article>
  );
}

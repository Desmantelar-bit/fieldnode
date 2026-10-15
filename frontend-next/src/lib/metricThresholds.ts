/**
 * metricThresholds.ts — fonte única dos limiares operacionais dos gráficos.
 *
 * Os valores abaixo já eram aplicados em HistoryChart (página de detalhes).
 * Foram extraídos sem nenhuma alteração de regra de negócio para que a
 * mini-sparkline dos KPIs use exatamente a mesma referência visual.
 */

export type MetricKey = 'temperatura' | 'vibracao' | 'rpm';

export type MetricThresholds = {
  /** Limite de atenção — linha pontilhada âmbar. */
  alert: number;
  /** Limite crítico — linha pontilhada vermelha. */
  critical: number;
  unit: string;
  /** true = quanto maior, pior (temperatura e vibração). */
  higherIsWorse: boolean;
  min: number;
  max: number;
};

export const METRIC_THRESHOLDS: Record<MetricKey, MetricThresholds> = {
  temperatura: { alert: 95,  critical: 110,  unit: '°C',  higherIsWorse: true,  min: 0, max: 150  },
  vibracao:    { alert: 0.5, critical: 0.8,  unit: 'g',   higherIsWorse: true,  min: 0, max: 10   },
  rpm:         { alert: 1400, critical: 1200, unit: 'rpm', higherIsWorse: false, min: 0, max: 3000 },
};

/**
 * Limiares que fazem sentido desenhar para a série informada.
 * Um limite distante da leitura atual é omitido para que a linha não fique achatada.
 */
export function visibleThresholds(values: number[], key: MetricKey) {
  const config = METRIC_THRESHOLDS[key];
  const finite = values.filter(Number.isFinite);

  if (!finite.length) {
    return { config, alert: null as number | null, critical: null as number | null };
  }

  const min = Math.min(...finite);
  const max = Math.max(...finite);
  const span = max - min || Math.abs(max) * 0.2 || 1;
  const window = span * 1.5;
  const inWindow = (value: number) => value >= min - window && value <= max + window;

  return {
    config,
    alert: inWindow(config.alert) ? config.alert : null,
    critical: inWindow(config.critical) ? config.critical : null,
  };
}

/** Limite da faixa normal (o lado oposto ao risco) para a série informada. */
export function normalBand(values: number[], key: MetricKey) {
  const { config, alert } = visibleThresholds(values, key);
  if (alert === null) return null;
  const finite = values.filter(Number.isFinite);
  const min = finite.length ? Math.min(...finite) : 0;
  const max = finite.length ? Math.max(...finite) : 1;
  const margin = (max - min) * 0.12 || Math.max(Math.abs(max) * 0.1, 1);
  const domainMin = Math.min(min - margin, alert);
  const domainMax = Math.max(max + margin, alert);
  return config.higherIsWorse
    ? { from: domainMin, to: alert }
    : { from: alert, to: domainMax };
}

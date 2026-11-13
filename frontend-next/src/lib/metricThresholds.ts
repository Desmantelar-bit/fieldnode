/** Generated from contracts/severity.v1.json. Do not edit by hand. */
export type MetricKey = 'temperatura' | 'vibracao' | 'rpm';
export type MetricThresholds = { alert: number | null; critical: number | null; unit: string; higherIsWorse: boolean; min: number; max: number };
export const METRIC_THRESHOLDS: Record<MetricKey, MetricThresholds> = {
  temperatura: { alert: 75.0, critical: 85.0, unit: "C", higherIsWorse: true, min: 0, max: 150 },
  vibracao: { alert: 5.0, critical: 8.0, unit: "indice_0_10", higherIsWorse: true, min: 0, max: 10 },
  rpm: { alert: null, critical: null, unit: "rpm", higherIsWorse: true, min: 0, max: 5000 },
};

export function visibleThresholds(values: number[], key: MetricKey) {
  const config = METRIC_THRESHOLDS[key];
  const finite = values.filter(Number.isFinite);
  if (!finite.length) return { config, alert: null as number | null, critical: null as number | null };
  const min = Math.min(...finite), max = Math.max(...finite);
  const span = max - min || Math.abs(max) * 0.2 || 1, window = span * 1.5;
  const inWindow = (value: number | null) => value !== null && value >= min - window && value <= max + window;
  return { config, alert: inWindow(config.alert) ? config.alert : null, critical: inWindow(config.critical) ? config.critical : null };
}

export function classifyMetric(key: MetricKey, value: number): 'NORMAL' | 'ATENCAO' | 'CRITICO' {
  const metric = METRIC_THRESHOLDS[key];
  if (!Number.isFinite(value) || value < metric.min || value > metric.max) throw new RangeError(`Valor inválido para ${key}`);
  if (metric.critical !== null && value >= metric.critical) return 'CRITICO';
  if (metric.alert !== null && value >= metric.alert) return 'ATENCAO';
  return 'NORMAL';
}

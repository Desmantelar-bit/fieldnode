/** Generated from contracts/severity.v1.json. Do not edit by hand. */
export type MetricKey = 'temperatura' | 'vibracao' | 'rpm';
export type MetricThresholds = {
  alert: number | null;
  critical: number | null;
  unit: string;
  higherIsWorse: boolean;
  min: number;
  max: number;
  severity: 'fixed' | 'dependente_de_regime';
};
export const METRIC_THRESHOLDS: Record<MetricKey, MetricThresholds> = {
  temperatura: { alert: 75.0, critical: 85.0, unit: "C", higherIsWorse: true, min: 0, max: 150, severity: 'fixed' },
  vibracao: { alert: 5.0, critical: 8.0, unit: "indice_0_10", higherIsWorse: true, min: 0, max: 10, severity: 'fixed' },
  rpm: { alert: null, critical: null, unit: "rpm", higherIsWorse: true, min: 0, max: 5000, severity: 'dependente_de_regime' },
};

export function visibleThresholds(values: number[], key: MetricKey) {
  const config = METRIC_THRESHOLDS[key];
  const finite = values.filter(Number.isFinite);
  if (!finite.length) return { config, alert: null as number | null, critical: null as number | null };
  const min = Math.min(...finite), max = Math.max(...finite);
  const span = max - min || Math.abs(max) * 0.2 || 1;
  const inWindow = (value: number | null) => value !== null && value >= min - span * 1.5 && value <= max + span * 1.5;
  return { config, alert: inWindow(config.alert) ? config.alert : null, critical: inWindow(config.critical) ? config.critical : null };
}

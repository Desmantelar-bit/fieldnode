/**
 * metrics.ts — fonte única da leitura de telemetria para os gráficos.
 *
 * Antes, a regra "esta leitura está boa / em atenção / crítica" e a montagem da
 * série temporal viviam duplicadas dentro de DashboardMachineData e de
 * HistoryChart. Como agora existem mais gráficos (área, linha e colunas), a
 * lógica foi centralizada aqui para os três consumirem exatamente a mesma
 * classificação — e os limiares continuam vindo de `metricThresholds`.
 */

import { METRIC_THRESHOLDS, type MetricKey } from '@/lib/metricThresholds';
import type { Telemetry } from '@/types/telemetry';

export type MetricStatus = 'normal' | 'atencao' | 'critico';

export type MetricMeta = {
  /** Nome completo, usado em cabeçalho e aria-label. */
  label: string;
  /** Nome curto, para as pílulas de troca de métrica. */
  short: string;
  unit: string;
  /** Cor da SÉRIE (família verde/ciano, para não competir com as linhas de limite). */
  color: string;
  /** Quantas casas decimais a métrica pede. */
  digits: number;
};

/** Ordem de exibição — a mesma em todos os gráficos do app. */
export const METRIC_ORDER: MetricKey[] = ['rpm', 'temperatura', 'vibracao'];

export const METRIC_META: Record<MetricKey, MetricMeta> = {
  rpm: {
    label: 'RPM do motor',
    short: 'RPM',
    unit: 'rpm',
    color: 'var(--metric-rpm)',
    digits: 0,
  },
  temperatura: {
    label: 'Temperatura do motor',
    short: 'Temperatura',
    unit: '°C',
    color: 'var(--metric-temperature)',
    digits: 1,
  },
  vibracao: {
    label: 'Vibração do rotor',
    short: 'Vibração',
    unit: 'g',
    color: 'var(--metric-vibration)',
    digits: 2,
  },
};

/** Cor semântica de cada faixa — a mesma das pílulas e das legendas do app. */
export const STATUS_COLOR: Record<MetricStatus, string> = {
  normal: 'var(--status-normal)',
  atencao: 'var(--status-atencao)',
  critico: 'var(--status-critico)',
};

export const STATUS_LABEL: Record<MetricStatus, string> = {
  normal: 'Normal',
  atencao: 'Atenção',
  critico: 'Crítico',
};

/**
 * Classifica um valor usando os limiares da métrica.
 * `higherIsWorse` decide o lado do limite (temperatura/vibração sobem o risco;
 * RPM cai para risco).
 */
export function statusOf(value: number, key: MetricKey): MetricStatus {
  const config = METRIC_THRESHOLDS[key];
  if (!Number.isFinite(value)) return 'normal';

  if (config.higherIsWorse) {
    if (value > config.critical) return 'critico';
    if (value > config.alert) return 'atencao';
    return 'normal';
  }

  if (value < config.critical) return 'critico';
  if (value < config.alert) return 'atencao';
  return 'normal';
}

export type MetricPoint = {
  /** Rótulo curto do eixo X (hora:minuto). */
  label: string;
  /** Rótulo completo, para o tooltip. */
  full: string;
  valor: number;
  status: MetricStatus;
};

/**
 * Monta a série da métrica na ordem de leitura do gráfico (antigo → recente).
 * A API entrega as leituras da mais nova para a mais antiga, por isso o
 * `reverse()` no fim.
 */
export function buildPoints(readings: Telemetry[], key: MetricKey): MetricPoint[] {
  return readings
    .map((reading) => {
      const valor = Number(reading[key]);
      const raw = reading.timestamp ? new Date(reading.timestamp) : null;
      const valid = raw !== null && !Number.isNaN(raw.getTime());
      return {
        valor,
        label: valid ? raw.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '',
        full: valid ? raw.toLocaleString('pt-BR') : 'Leitura sem data',
        status: statusOf(valor, key),
      };
    })
    .filter((point) => Number.isFinite(point.valor))
    .reverse();
}

export type MetricSummary = {
  count: number;
  min: number;
  max: number;
  avg: number;
  /** Quantas leituras caíram fora da faixa normal. */
  foraDaFaixa: number;
};

export function summarize(points: MetricPoint[]): MetricSummary {
  if (!points.length) {
    return { count: 0, min: 0, max: 0, avg: 0, foraDaFaixa: 0 };
  }

  const values = points.map((point) => point.valor);
  return {
    count: values.length,
    min: Math.min(...values),
    max: Math.max(...values),
    avg: values.reduce((acc, value) => acc + value, 0) / values.length,
    foraDaFaixa: points.filter((point) => point.status !== 'normal').length,
  };
}

export function formatMetric(value: number, key: MetricKey): string {
  const { digits } = METRIC_META[key];
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

/**
 * Formata um LIMITE (alerta/risco) na precisão da métrica: limites são números
 * redondos, então não faz sentido escrever "1.400,0 rpm" — mas a vibração
 * precisa da casa decimal para o 0,5 g ficar legível.
 *
 * Use esta função para LIMITES, nunca para marcas de eixo ou leituras: o
 * `Math.max(digits, 1)` abaixo foi feito para o 0,5 g, mas aplicado a um eixo de
 * RPM ele imprimia "2.444,1 rpm" — uma precisão que o sensor não entrega.
 */
export function formatLimit(value: number, key: MetricKey): string {
  const { digits } = METRIC_META[key];
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: Math.max(digits, 1),
  }).format(value);
}

/**
 * Formata uma marca do EIXO de um gráfico, na precisão exata da métrica.
 *
 * Separada de `formatLimit` de propósito: o eixo de RPM é contagem inteira
 * (1.177 · 1.527 · 2.444) e o de temperatura tem uma casa (96,9), enquanto o
 * limite de vibração precisa de uma casa mesmo sendo "0,5". Três regras
 * diferentes, três funções — antes uma só tentava servir as três.
 */
export function formatAxis(value: number, key: MetricKey): string {
  const { digits } = METRIC_META[key];
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  }).format(value);
}

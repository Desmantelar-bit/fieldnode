'use client';

import {
  Activity, AlertTriangle, ArrowUpRight, CheckCircle2,
  Clock3, Gauge, Leaf, LineChart, ShieldCheck,
} from 'lucide-react';
import type { Relatorio } from '@/types/telemetry';
import { fieldLabel, primaryButton, secondaryButton } from '@/lib/design-tokens';

type ReportPreviewProps = {
  relatorio: Relatorio;
  machineLabel: string;
  onExport: () => void;
  exporting: boolean;
};

type Metric = {
  label: string;
  value: string;
  context: string;
  tone: 'neutral' | 'positive' | 'warning';
  icon: typeof Activity;
};

function getReportReadout(relatorio: Relatorio) {
  if (relatorio.alertas_gerados === 0) {
    return {
      title: 'Janela sem anomalias registradas',
      body:  'A telemetria consolidada não registrou alertas no período selecionado.',
      tone:  'positive' as const,
    };
  }
  if (relatorio.eficiencia_operacional >= 85) {
    return {
      title: 'Operação estável com pontos de atenção',
      body:  `${relatorio.alertas_gerados} alerta(s) registrado(s), mas o índice operacional permaneceu alto.`,
      tone:  'warning' as const,
    };
  }
  return {
    title: 'Revisão operacional recomendada',
    body:  `${relatorio.alertas_gerados} alerta(s) e índice de ${relatorio.eficiencia_operacional.toFixed(1)}% pedem acompanhamento.`,
    tone:  'warning' as const,
  };
}

export function ReportPreview({ relatorio, machineLabel, onExport, exporting }: ReportPreviewProps) {
  const readout    = getReportReadout(relatorio);
  const efficiency = Math.max(0, Math.min(100, relatorio.eficiencia_operacional));

  const metrics: Metric[] = [
    {
      label:   'Leituras analisadas',
      value:   new Intl.NumberFormat('pt-BR').format(relatorio.total_leituras),
      context: 'volume consolidado',
      tone:    'neutral',
      icon:    Activity,
    },
    {
      label:   'Máquinas ativas',
      value:   String(relatorio.maquinas_ativas),
      context: 'com telemetria no período',
      tone:    'positive',
      icon:    Gauge,
    },
    {
      label:   'Alertas gerados',
      value:   String(relatorio.alertas_gerados),
      context: 'anomalias identificadas',
      tone:    relatorio.alertas_gerados > 0 ? 'warning' : 'positive',
      icon:    AlertTriangle,
    },
  ];

  const metricCardClass = (tone: Metric['tone']) => {
    if (tone === 'neutral')  return 'border-[var(--line)] bg-[var(--panel-glass-mid)]';
    if (tone === 'positive') return 'border-[color:var(--status-normal)]/20 bg-[color:var(--status-normal)]/6';
    return 'border-[color:var(--status-atencao)]/20 bg-[color:var(--status-atencao)]/6';
  };

  const metricValueClass = (tone: Metric['tone']) => {
    if (tone === 'positive') return 'text-[color:var(--status-normal)]';
    if (tone === 'warning')  return 'text-[color:var(--status-atencao)]';
    return 'text-[var(--text-1)]';
  };

  return (
    <section
      className="report-sheet"
      aria-labelledby="report-preview-title"
    >
      {/* Header */}
      <div className="border-b border-[var(--line)] px-5 py-5 sm:px-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[var(--panel-glass-strong)] text-[color:var(--ui-accent)]">
              <LineChart size={20} strokeWidth={1.8} aria-hidden="true" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className={fieldLabel}>Relatório executivo</p>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-[color:var(--status-normal)]/25 bg-[color:var(--status-normal)]/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.1em] text-[color:var(--status-normal)]">
                  <span className="h-1.5 w-1.5 rounded-full bg-current" /> Pronto
                </span>
              </div>
              <h2 id="report-preview-title" className="mt-1.5 text-lg font-bold tracking-tight text-[var(--text-1)] sm:text-xl">
                {machineLabel}
              </h2>
              <p className="mt-0.5 text-xs text-[var(--text-3)]">
                {relatorio.periodo} · consolidação da telemetria
              </p>
            </div>
          </div>
          <button type="button" onClick={onExport} disabled={exporting} className={primaryButton}>
            <ArrowUpRight size={15} aria-hidden="true" />
            {exporting ? 'Preparando...' : 'Exportar XLSX'}
          </button>
        </div>
      </div>

      <div className="space-y-6 px-5 py-5 sm:px-6">
        {/* Métricas */}
        <div className="grid gap-3 sm:grid-cols-3">
          {metrics.map(({ label, value, context, tone, icon: Icon }) => (
            <article
              key={label}
              className={`report-metric rounded-xl border ${metricCardClass(tone)}`}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
                  {label}
                </p>
                <Icon size={14} strokeWidth={1.8} className="text-[var(--text-3)]" aria-hidden="true" />
              </div>
              <p className={`report-metric__value mt-3 text-2xl font-bold tracking-tight ${metricValueClass(tone)}`}>
                {value}
              </p>
              <p className="mt-0.5 text-[10px] text-[var(--text-3)]">{context}</p>
            </article>
          ))}
        </div>

        {/* Leitura + Eficiência */}
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_16rem]">
          <div className="rounded-xl bg-[var(--panel-glass-mid)] p-4 sm:p-5">
            <div className="flex items-start gap-3">
              <div className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ${
                readout.tone === 'positive'
                  ? 'bg-[color:var(--status-normal)]/10 text-[color:var(--status-normal)]'
                  : 'bg-[color:var(--status-atencao)]/10 text-[color:var(--status-atencao)]'
              }`}>
                {readout.tone === 'positive'
                  ? <ShieldCheck size={16} aria-hidden="true" />
                  : <AlertTriangle size={16} aria-hidden="true" />
                }
              </div>
              <div>
                <p className={fieldLabel}>Leitura do período</p>
                <h3 className="mt-1 text-sm font-bold text-[var(--text-1)]">{readout.title}</h3>
                <p className="mt-1.5 text-xs leading-relaxed text-[var(--text-3)]">{readout.body}</p>
              </div>
              <Clock3 size={16} className="hidden shrink-0 text-[var(--text-3)] sm:block" aria-hidden="true" />
            </div>
          </div>

          <div className="report-metric rounded-xl bg-[var(--panel-glass-mid)]">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <p className={fieldLabel}>Eficiência operacional</p>
                <p className="report-metric__value mt-2 text-3xl font-bold tracking-tight text-[var(--text-1)]">
                  {relatorio.eficiencia_operacional.toFixed(1)}%
                </p>
              </div>
              <Leaf size={20} strokeWidth={1.8} className="shrink-0 text-[color:var(--status-normal)]" aria-hidden="true" />
            </div>
            <div
              className="mt-4 h-1.5 overflow-hidden rounded-full bg-[var(--panel-glass-strong)]"
              aria-label={`Eficiência de ${relatorio.eficiencia_operacional.toFixed(1)}%`}
            >
              <div
                className="h-full rounded-full bg-[color:var(--status-normal)] transition-[width] duration-500"
                style={{ width: `${efficiency}%` }}
              />
            </div>
            <p className="mt-2.5 text-[10px] leading-relaxed text-[var(--text-3)]">
              Índice consolidado das leituras no recorte selecionado.
            </p>
          </div>
        </div>

        {/* Tabela */}
        <div>
          <div className="mb-3 flex items-end justify-between gap-4">
            <div>
              <p className={fieldLabel}>Quadro de indicadores</p>
              <h3 className="mt-1 text-sm font-bold text-[var(--text-1)]">Resumo operacional</h3>
            </div>
          </div>

          <div className="hidden md:block">
            <table className="report-table">
              <thead>
                <tr>
                  <th>Métrica</th>
                  <th>Valor</th>
                  <th>Contexto</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map(({ label, value, context, tone }) => (
                  <tr key={label}>
                    <td className="font-semibold text-[var(--text-1)]">{label}</td>
                    <td className={`font-bold ${metricValueClass(tone)}`}>{value}</td>
                    <td className="text-xs">{context}</td>
                    <td className="text-right">
                      <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] ${
                        tone === 'warning'
                          ? 'border-[color:var(--status-atencao)]/20 bg-[color:var(--status-atencao)]/8 text-[color:var(--status-atencao)]'
                          : 'border-[color:var(--status-normal)]/20 bg-[color:var(--status-normal)]/8 text-[color:var(--status-normal)]'
                      }`}>
                        consolidado
                      </span>
                    </td>
                  </tr>
                ))}
                <tr>
                  <td className="font-semibold text-[var(--text-1)]">Eficiência operacional</td>
                  <td className="font-bold text-[color:var(--status-normal)]">{relatorio.eficiencia_operacional.toFixed(1)}%</td>
                  <td className="text-xs">índice operacional consolidado</td>
                  <td className="text-right">
                    <span className="inline-flex rounded-full border border-[color:var(--status-normal)]/20 bg-[color:var(--status-normal)]/8 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-[color:var(--status-normal)]">
                      consolidado
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Mobile */}
          <div className="space-y-2 md:hidden">
            {[
              ...metrics.map(({ label, value, context, tone }) => ({ label, value, context, tone })),
              { label: 'Eficiência operacional', value: `${relatorio.eficiencia_operacional.toFixed(1)}%`, context: 'índice operacional consolidado', tone: 'positive' as const },
            ].map(({ label, value, context, tone }) => (
              <article key={label} className="rounded-xl bg-[var(--panel-glass-mid)] p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-semibold text-[var(--text-1)]">{label}</p>
                  <p className={`text-lg font-bold ${metricValueClass(tone)}`}>{value}</p>
                </div>
                <p className="mt-1 text-[10px] text-[var(--text-3)]">{context}</p>
              </article>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex flex-col gap-3 border-t border-[var(--line)] pt-4 text-xs text-[var(--text-3)] sm:flex-row sm:items-center sm:justify-between">
          <p className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-[color:var(--status-normal)]" aria-hidden="true" />
            Pronto para apresentação e compartilhamento
          </p>
          <button type="button" onClick={onExport} disabled={exporting} className={secondaryButton}>
            <ArrowUpRight size={14} aria-hidden="true" /> Baixar cópia
          </button>
        </div>
      </div>
    </section>
  );
}

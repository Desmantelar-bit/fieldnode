'use client';

import { Activity, AlertTriangle, ArrowUpRight, CheckCircle2, Clock3, Gauge, Leaf, LineChart, ShieldCheck } from 'lucide-react';
import type { Relatorio } from '@/types/telemetry';
import { fieldLabel, lightCard, primaryButton, secondaryButton } from '@/lib/design-tokens';

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
  tone: 'dark' | 'green' | 'amber';
  icon: typeof Activity;
};

function getReportReadout(relatorio: Relatorio) {
  if (relatorio.alertas_gerados === 0) {
    return {
      title: 'janela sem anomalias registradas',
      body: 'a telemetria consolidada não registrou alertas no período selecionado.',
      tone: 'green' as const,
    };
  }

  if (relatorio.eficiencia_operacional >= 85) {
    return {
      title: 'operação estável com pontos de atenção',
      body: `${relatorio.alertas_gerados} alerta(s) foram registrados, mas o índice operacional permaneceu alto.`,
      tone: 'amber' as const,
    };
  }

  return {
    title: 'revisão operacional recomendada',
    body: `${relatorio.alertas_gerados} alerta(s) e um índice de ${relatorio.eficiencia_operacional.toFixed(1)}% pedem acompanhamento da equipe.`,
    tone: 'amber' as const,
  };
}

export function ReportPreview({ relatorio, machineLabel, onExport, exporting }: ReportPreviewProps) {
  const readout = getReportReadout(relatorio);
  const efficiency = Math.max(0, Math.min(100, relatorio.eficiencia_operacional));

  const metrics: Metric[] = [
    {
      label: 'Leituras analisadas',
      value: new Intl.NumberFormat('pt-BR').format(relatorio.total_leituras),
      context: 'volume consolidado',
      tone: 'dark',
      icon: Activity,
    },
    {
      label: 'Máquinas ativas',
      value: String(relatorio.maquinas_ativas),
      context: 'com telemetria no período',
      tone: 'green',
      icon: Gauge,
    },
    {
      label: 'Alertas gerados',
      value: String(relatorio.alertas_gerados),
      context: 'anomalias identificadas',
      tone: relatorio.alertas_gerados > 0 ? 'amber' : 'green',
      icon: AlertTriangle,
    },
  ];

  return (
    <section className={`${lightCard} overflow-hidden`} aria-labelledby="report-preview-title">
      <div className="border-b border-slate-200 px-5 py-6 sm:px-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-lime-300 shadow-lg shadow-slate-950/10">
              <LineChart aria-hidden="true" size={21} strokeWidth={1.8} />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className={fieldLabel}>relatório executivo</p>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.12em] text-emerald-800">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> pronto para leitura
                </span>
              </div>
              <h2 id="report-preview-title" className="mt-2 text-xl font-bold tracking-tight text-slate-950 sm:text-2xl">
                {machineLabel}
              </h2>
              <p className="mt-1 text-sm text-slate-500">{relatorio.periodo} · consolidação da telemetria do campo</p>
            </div>
          </div>

          <button type="button" onClick={onExport} disabled={exporting} className={primaryButton}>
            <ArrowUpRight aria-hidden="true" size={16} />
            {exporting ? 'preparando xlsx...' : 'exportar xlsx'}
          </button>
        </div>
      </div>

      <div className="space-y-8 px-5 py-6 sm:px-8 sm:py-8">
        <div className="grid gap-3 sm:grid-cols-3 sm:gap-4">
          {metrics.map(({ label, value, context, tone, icon: Icon }) => (
            <article
              key={label}
              className={`rounded-2xl border p-4 ${
                tone === 'dark'
                  ? 'border-slate-950 bg-slate-950 text-white'
                  : tone === 'amber'
                    ? 'border-amber-200 bg-amber-50 text-amber-950'
                    : 'border-emerald-200 bg-emerald-50 text-emerald-950'
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <p className={`text-xs font-semibold ${tone === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>{label}</p>
                <Icon aria-hidden="true" size={16} strokeWidth={1.8} />
              </div>
              <p className="mt-5 text-3xl font-bold tracking-tight">{value}</p>
              <p className={`mt-1 text-xs ${tone === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>{context}</p>
            </article>
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_18rem]">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="flex gap-3">
                <div className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${readout.tone === 'green' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                  {readout.tone === 'green' ? <ShieldCheck aria-hidden="true" size={18} /> : <AlertTriangle aria-hidden="true" size={18} />}
                </div>
                <div>
                  <p className={fieldLabel}>leitura do período</p>
                  <h3 className="mt-1 text-base font-bold text-slate-950">{readout.title}</h3>
                  <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600">{readout.body}</p>
                </div>
              </div>
              <Clock3 aria-hidden="true" className="hidden shrink-0 text-slate-300 sm:block" size={19} />
            </div>
          </div>

          <div className="rounded-2xl bg-slate-100 p-5 sm:p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className={fieldLabel}>eficiência operacional</p>
                <p className="mt-2 text-3xl font-bold tracking-tight text-slate-950">{relatorio.eficiencia_operacional.toFixed(1)}%</p>
              </div>
              <Leaf aria-hidden="true" className="text-emerald-600" size={21} strokeWidth={1.8} />
            </div>
            <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-200" aria-label={`Eficiência operacional de ${relatorio.eficiencia_operacional.toFixed(1)} por cento`}>
              <div className="h-full rounded-full bg-emerald-500 transition-[width] duration-500" style={{ width: `${efficiency}%` }} />
            </div>
            <p className="mt-3 text-xs leading-relaxed text-slate-500">Índice consolidado a partir das leituras disponíveis no recorte.</p>
          </div>
        </div>

        <div>
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <p className={fieldLabel}>quadro de indicadores</p>
              <h3 className="mt-1 text-base font-bold text-slate-950">Resumo operacional</h3>
            </div>
            <span className="hidden text-xs text-slate-400 sm:block">visualização compacta para banca e operação</span>
          </div>

          <div className="hidden overflow-hidden rounded-2xl border border-slate-200 md:block">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100 text-[11px] uppercase tracking-[0.14em] text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-semibold">métrica</th>
                  <th className="px-5 py-3 font-semibold">valor</th>
                  <th className="px-5 py-3 font-semibold">contexto</th>
                  <th className="px-5 py-3 text-right font-semibold">status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {metrics.map(({ label, value, context, tone }) => (
                  <tr key={label} className="transition hover:bg-slate-50">
                    <td className="px-5 py-4 font-semibold text-slate-950">{label}</td>
                    <td className="px-5 py-4 font-bold text-slate-950">{value}</td>
                    <td className="px-5 py-4">{context}</td>
                    <td className="px-5 py-4 text-right">
                      <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${tone === 'amber' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
                        consolidado
                      </span>
                    </td>
                  </tr>
                ))}
                <tr className="bg-slate-50">
                  <td className="px-5 py-4 font-semibold text-slate-950">Eficiência operacional</td>
                  <td className="px-5 py-4 font-bold text-slate-950">{relatorio.eficiencia_operacional.toFixed(1)}%</td>
                  <td className="px-5 py-4">índice operacional consolidado</td>
                  <td className="px-5 py-4 text-right"><span className="inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800">consolidado</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="space-y-3 md:hidden">
            {[
              ...metrics.map(({ label, value, context }) => ({ label, value, context })),
              { label: 'Eficiência operacional', value: `${relatorio.eficiencia_operacional.toFixed(1)}%`, context: 'índice operacional consolidado' },
            ].map(({ label, value, context }) => (
              <article key={label} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex items-center justify-between gap-4">
                  <p className="text-sm font-semibold text-slate-950">{label}</p>
                  <p className="text-lg font-bold text-slate-950">{value}</p>
                </div>
                <p className="mt-2 text-xs text-slate-500">{context}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3 border-t border-slate-200 pt-5 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <p className="flex items-center gap-2"><CheckCircle2 aria-hidden="true" className="text-emerald-600" size={15} /> pronto para apresentação e compartilhamento</p>
          <button type="button" onClick={onExport} disabled={exporting} className={secondaryButton}>
            <ArrowUpRight aria-hidden="true" size={15} /> baixar cópia
          </button>
        </div>
      </div>
    </section>
  );
}

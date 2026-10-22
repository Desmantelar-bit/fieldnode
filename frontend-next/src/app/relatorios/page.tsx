'use client';

import { useEffect, useState } from 'react';
import { CalendarRange, FileText, RefreshCw, SlidersHorizontal } from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { ReportPreview } from '@/components/ReportPreview';
import { telemetryService } from '@/services/telemetryService';
import type { EstadoRequisicao } from '@/types/api';
import type { Relatorio } from '@/types/telemetry';

type MachineOption = { id: number; maquina_id: string; modelo: string; marca: string };
type ExportState = 'idle' | 'loading' | 'error';

const PERIOD_OPTIONS = [
  { label: 'Últimos 7 dias',  value: 7 },
  { label: 'Últimos 15 dias', value: 15 },
  { label: 'Últimos 30 dias', value: 30 },
];

function downloadBlob(blob: Blob, machineId: string) {
  const url    = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href     = url;
  anchor.download = `fieldnode_relatorio_${machineId}_${new Date().toISOString().slice(0, 10)}.xlsx`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => window.URL.revokeObjectURL(url), 0);
}

const selectClass =
  'min-h-11 w-full rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] px-4 text-sm font-medium text-[var(--text-1)] outline-none transition hover:border-[var(--border-highlight)] focus:border-[color:var(--ui-accent)]/60 disabled:cursor-not-allowed disabled:opacity-50';

export default function RelatoriosPage() {
  const [estadoMaquinas,  setEstadoMaquinas]  = useState<EstadoRequisicao<MachineOption[]>>({ tipo: 'carregando' });
  const [selectedMachine, setSelectedMachine] = useState('');
  const [period,          setPeriod]          = useState(7);
  const [estadoRelatorio, setEstadoRelatorio] = useState<EstadoRequisicao<Relatorio>>({ tipo: 'vazio' });
  const [exportState,        setExportState]        = useState<ExportState>('idle');
  const [exportErrorMessage, setExportErrorMessage] = useState('');

  useEffect(() => {
    let active = true;
    telemetryService.getFleetStatus()
      .then((machines) => {
        if (!active) return;
        const options = machines
          .filter((m) => m.maquina_id)
          .map((m) => ({ id: m.id, maquina_id: m.maquina_id ?? '', modelo: m.modelo.nome, marca: m.modelo.marca.nome }));
        setEstadoMaquinas(options.length ? { tipo: 'sucesso', dados: options } : { tipo: 'vazio' });
        setSelectedMachine(options[0]?.maquina_id ?? '');
      })
      .catch((err: unknown) => {
        if (active) setEstadoMaquinas({ tipo: 'erro', mensagem: err instanceof Error ? err.message : 'Não foi possível carregar a frota.' });
      });
    return () => { active = false; };
  }, []);

  const selectedOption  = estadoMaquinas.tipo === 'sucesso' ? estadoMaquinas.dados.find((m) => m.maquina_id === selectedMachine) : undefined;
  const machineLabel    = selectedOption ? `${selectedOption.maquina_id} · ${selectedOption.marca} ${selectedOption.modelo}` : selectedMachine || 'máquina selecionada';
  const relatorio       = estadoRelatorio.tipo === 'sucesso' ? estadoRelatorio.dados : null;

  const handleGenerate = async () => {
    if (!selectedMachine) return;
    setEstadoRelatorio({ tipo: 'carregando' });
    try {
      const data = await telemetryService.getRelatorio({ machineId: selectedMachine, period });
      if (data.status && data.status !== 'ok') throw new Error(data.detalhe || 'Sem dados para o período selecionado.');
      setEstadoRelatorio({ tipo: 'sucesso', dados: data });
    } catch (err) {
      setEstadoRelatorio({ tipo: 'erro', mensagem: err instanceof Error ? err.message : 'Não foi possível gerar o relatório.' });
    }
  };

  const handleExport = async () => {
    if (!selectedMachine || exportState === 'loading') return;
    setExportState('loading');
    setExportErrorMessage('');
    try {
      const blob = await telemetryService.exportReport(selectedMachine);
      downloadBlob(blob, selectedMachine);
      setExportState('idle');
    } catch (err) {
      setExportErrorMessage(err instanceof Error ? err.message : 'Não foi possível preparar o arquivo. Verifique a conexão com a API e tente novamente.');
      setExportState('error');
    }
  };

  return (
    <AppShell
      active="/relatorios"
      eyebrow="Inteligência operacional"
      title="Relatórios"
      description="Consolide telemetria, alertas e eficiência em uma leitura clara da operação."
    >

        {/* Filtros */}
        <section
          className="metric-card mb-6"
          aria-labelledby="report-filters-title"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[var(--panel-glass-strong)] text-[color:var(--ui-accent)]">
              <SlidersHorizontal size={16} strokeWidth={1.8} aria-hidden="true" />
            </div>
            <div>
              <h2
                id="report-filters-title"
                className="text-sm font-bold text-[var(--text-1)]"
              >
                Configurar leitura
              </h2>
              <p className="text-[10px] text-[var(--text-3)]">
                Selecione máquina e período
              </p>
            </div>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-[minmax(0,1fr)_11rem_auto] md:items-end">
            <label className="grid gap-1.5">
              <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
                Máquina
              </span>
              <select
                value={selectedMachine}
                onChange={(e) => { setSelectedMachine(e.target.value); setEstadoRelatorio({ tipo: 'vazio' }); }}
                disabled={estadoMaquinas.tipo !== 'sucesso'}
                className={selectClass}
              >
                {estadoMaquinas.tipo === 'sucesso' && estadoMaquinas.dados.map((m) => (
                  <option key={m.id} value={m.maquina_id}>
                    {m.maquina_id} · {m.marca} {m.modelo}
                  </option>
                ))}
              </select>
            </label>

            <label className="grid gap-1.5">
              <span className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
                <CalendarRange size={11} aria-hidden="true" /> Período
              </span>
              <select
                value={period}
                onChange={(e) => { setPeriod(Number(e.target.value)); setEstadoRelatorio({ tipo: 'vazio' }); }}
                className={selectClass}
              >
                {PERIOD_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </label>

            <button
              type="button"
              onClick={handleGenerate}
              disabled={!selectedMachine || estadoRelatorio.tipo === 'carregando'}
              className="btn-brand inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-5 text-sm font-bold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] disabled:cursor-not-allowed"
            >
              <RefreshCw
                size={15}
                aria-hidden="true"
                className={estadoRelatorio.tipo === 'carregando' ? 'animate-spin' : ''}
              />
              {estadoRelatorio.tipo === 'carregando' ? 'Gerando...' : 'Gerar leitura'}
            </button>
          </div>
        </section>

        {/* Estados de carregamento / erro / vazio */}
        {estadoMaquinas.tipo === 'carregando' && (
          <div className="metric-card animate-pulse" aria-label="Carregando lista de máquinas">
            <div className="h-3 w-28 rounded-full bg-[var(--panel-glass-strong)]" />
            <div className="mt-4 h-10 max-w-sm rounded-xl bg-[var(--panel-glass-strong)]" />
            <div className="mt-6 grid gap-4 sm:grid-cols-3">
              {[1, 2, 3].map((i) => <div key={i} className="h-24 rounded-xl bg-[var(--panel-glass-mid)]" />)}
            </div>
          </div>
        )}

        {estadoMaquinas.tipo === 'erro' && (
          <div className="metric-card border border-[color:var(--status-critico)]/20 bg-[color:var(--status-critico)]/5" role="alert">
            <p className="text-sm text-[color:var(--status-critico)]">
              Não foi possível carregar a frota. {estadoMaquinas.mensagem}
            </p>
          </div>
        )}

        {estadoMaquinas.tipo === 'vazio' && (
          <div className="metric-card py-10 text-center text-sm text-[var(--text-3)]">
            Nenhuma máquina cadastrada para gerar relatórios.
          </div>
        )}

        {estadoMaquinas.tipo === 'sucesso' && estadoRelatorio.tipo === 'erro' && (
          <div className="metric-card mb-4 border border-[color:var(--status-critico)]/20 bg-[color:var(--status-critico)]/5" role="alert">
            <p className="text-sm text-[color:var(--status-critico)]">
              Não foi possível gerar esta leitura. {estadoRelatorio.mensagem}
            </p>
          </div>
        )}

        {estadoMaquinas.tipo === 'sucesso' && estadoRelatorio.tipo === 'vazio' && (
          <div className="metric-card py-12">
            <div className="mx-auto max-w-sm text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--panel-glass-strong)] text-[color:var(--ui-accent)]">
                <FileText size={20} aria-hidden="true" />
              </div>
              <p className="mt-4 text-base font-bold text-[var(--text-1)]">
                Relatório em branco
              </p>
              <p className="mt-2 text-sm leading-relaxed text-[var(--text-3)]">
                Selecione uma máquina, escolha a janela de análise e gere o consolidado.
              </p>
            </div>
          </div>
        )}

        {relatorio && (
          <>
            <ReportPreview
              relatorio={relatorio}
              machineLabel={machineLabel}
              onExport={handleExport}
              exporting={exportState === 'loading'}
            />
            {exportState === 'error' && (
              <p className="mt-3 text-center text-xs text-[color:var(--status-critico)]" role="alert">
                {exportErrorMessage || 'Não foi possível preparar o arquivo. Verifique a conexão com a API e tente novamente.'}
              </p>
            )}
          </>
        )}
    </AppShell>
  );
}

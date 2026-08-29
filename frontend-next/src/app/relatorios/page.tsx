'use client';

import { useEffect, useState } from 'react';
import { CalendarRange, FileText, RefreshCw, Server, SlidersHorizontal } from 'lucide-react';
import { BackButton } from '@/components/BackButton';
import { ReportPreview } from '@/components/ReportPreview';
import { Sidebar } from '@/components/Sidebar';
import { telemetryService, resolveApiUrl } from '@/services/telemetryService';
import type { EstadoRequisicao } from '@/types/api';
import type { Relatorio } from '@/types/telemetry';

type MachineOption = { id: number; maquina_id: string; modelo: string; marca: string };

type ExportState = 'idle' | 'loading' | 'error';

const PERIOD_OPTIONS = [
  { label: 'últimos 7 dias', value: 7 },
  { label: 'últimos 15 dias', value: 15 },
  { label: 'últimos 30 dias', value: 30 },
];

function downloadBlob(blob: Blob, machineId: string) {
  const blobUrl = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = blobUrl;
  anchor.download = `fieldnode_relatorio_${machineId}_${new Date().toISOString().slice(0, 10)}.xlsx`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => window.URL.revokeObjectURL(blobUrl), 0);
}

export default function RelatoriosPage() {
  const [estadoMaquinas, setEstadoMaquinas] = useState<EstadoRequisicao<MachineOption[]>>({ tipo: 'carregando' });
  const [selectedMachine, setSelectedMachine] = useState('');
  const [period, setPeriod] = useState(7);
  const [estadoRelatorio, setEstadoRelatorio] = useState<EstadoRequisicao<Relatorio>>({ tipo: 'vazio' });
  const [exportState, setExportState] = useState<ExportState>('idle');

  useEffect(() => {
    let active = true;

    telemetryService.getFleetStatus()
      .then((machines) => {
        if (!active) return;
        const options = machines
          .filter((machine) => machine.maquina_id)
          .map((machine) => ({
            id: machine.id,
            maquina_id: machine.maquina_id ?? '',
            modelo: machine.modelo.nome,
            marca: machine.modelo.marca.nome,
          }));
        setEstadoMaquinas(options.length ? { tipo: 'sucesso', dados: options } : { tipo: 'vazio' });
        setSelectedMachine(options[0]?.maquina_id ?? '');
      })
      .catch((error: unknown) => {
        if (active) {
          setEstadoMaquinas({
            tipo: 'erro',
            mensagem: error instanceof Error ? error.message : 'não foi possível carregar a frota.',
          });
        }
      });

    return () => { active = false; };
  }, []);

  const selectedMachineOption = estadoMaquinas.tipo === 'sucesso'
    ? estadoMaquinas.dados.find((machine) => machine.maquina_id === selectedMachine)
    : undefined;
  const machineLabel = selectedMachineOption
    ? `${selectedMachineOption.maquina_id} · ${selectedMachineOption.marca} ${selectedMachineOption.modelo}`
    : selectedMachine || 'máquina selecionada';
  const relatorio = estadoRelatorio.tipo === 'sucesso' ? estadoRelatorio.dados : null;

  const handleGenerate = async () => {
    if (!selectedMachine) return;
    setEstadoRelatorio({ tipo: 'carregando' });
    try {
      const data = await telemetryService.getRelatorio({ machineId: selectedMachine, period });
      if (data.status && data.status !== 'ok') {
        throw new Error(data.detalhe || 'sem dados para o período selecionado.');
      }
      setEstadoRelatorio({ tipo: 'sucesso', dados: data });
    } catch (error) {
      setEstadoRelatorio({
        tipo: 'erro',
        mensagem: error instanceof Error ? error.message : 'não foi possível gerar o relatório.',
      });
    }
  };

  const handleExport = async () => {
    if (!selectedMachine || exportState === 'loading') return;
    setExportState('loading');
    try {
      const url = `${resolveApiUrl()}/relatorio/exportar/?maquina_id=${encodeURIComponent(selectedMachine)}`;
      const response = await fetch(url, { headers: { Accept: '*/*' } });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      downloadBlob(await response.blob(), selectedMachine);
      setExportState('idle');
    } catch {
      setExportState('error');
    }
  };

  return (
    <main className="min-h-screen bg-[image:var(--surface-page)] p-5 pb-28 text-field-text sm:p-8 sm:pb-32 lg:ml-28 lg:pb-12">
      <Sidebar />
      <BackButton />

      <div className="mx-auto max-w-7xl">
        <header className="mb-8 pl-14 lg:pl-0">
          <div className="flex flex-wrap items-center gap-3">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-accent">FieldNode / inteligência operacional</p>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-status-normal/20 bg-status-normal/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-status-normal">
              <span className="h-1.5 w-1.5 rounded-full bg-status-normal shadow-[0_0_8px_var(--glow-normal-strong)]" /> dados locais
            </span>
          </div>
          <h1 className="mt-3 max-w-3xl text-3xl font-semibold tracking-title text-field-text1 sm:text-4xl">relatórios que dão contexto ao campo</h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-field-text3 sm:text-base">Consolide telemetria, alertas e eficiência em uma leitura que serve tanto para a operação quanto para a banca. Sem planilha com cara de castigo.</p>
        </header>

        <section className="glass-panel mb-6 rounded-3xl p-4 sm:p-5" aria-labelledby="report-filters-title">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="flex gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white/[0.06] text-accent">
                <SlidersHorizontal aria-hidden="true" size={18} strokeWidth={1.8} />
              </div>
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-field-text3">configuração de leitura</p>
                <h2 id="report-filters-title" className="mt-1 text-sm font-semibold text-field-text1">Escolha o recorte da operação</h2>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-xs text-field-text3">
              <span className="inline-flex items-center gap-1.5"><Server aria-hidden="true" size={14} /> api django</span>
              <span className="text-field-border">/</span>
              <span className="inline-flex items-center gap-1.5"><CalendarRange aria-hidden="true" size={14} /> janela móvel</span>
            </div>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-[minmax(0,1fr)_12rem_auto] md:items-end">
            <label className="grid gap-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-field-text3">
              máquina
              <select
                value={selectedMachine}
                onChange={(event) => {
                  setSelectedMachine(event.target.value);
                  setEstadoRelatorio({ tipo: 'vazio' });
                }}
                disabled={estadoMaquinas.tipo !== 'sucesso'}
                className="min-h-12 w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 text-sm font-medium normal-case tracking-normal text-field-text1 outline-none transition hover:border-white/20 focus:border-accent/60 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {estadoMaquinas.tipo === 'sucesso' && estadoMaquinas.dados.map((machine) => (
                  <option key={machine.id} value={machine.maquina_id} className="bg-slate-950 text-white">{machine.maquina_id} · {machine.marca} {machine.modelo}</option>
                ))}
              </select>
            </label>

            <label className="grid gap-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-field-text3">
              período
              <select
                value={period}
                onChange={(event) => {
                  setPeriod(Number(event.target.value));
                  setEstadoRelatorio({ tipo: 'vazio' });
                }}
                className="min-h-12 w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 text-sm font-medium normal-case tracking-normal text-field-text1 outline-none transition hover:border-white/20 focus:border-accent/60"
              >
                {PERIOD_OPTIONS.map((option) => <option key={option.value} value={option.value} className="bg-slate-950 text-white">{option.label}</option>)}
              </select>
            </label>

            <button
              type="button"
              onClick={handleGenerate}
              disabled={!selectedMachine || estadoRelatorio.tipo === 'carregando'}
              className="inline-flex min-h-12 items-center justify-center gap-2 rounded-2xl bg-accent px-5 text-sm font-bold text-slate-950 shadow-[0_0_24px_var(--glow-normal)] transition hover:brightness-105 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.98]"
            >
              <RefreshCw aria-hidden="true" className={estadoRelatorio.tipo === 'carregando' ? 'animate-spin' : ''} size={16} />
              {estadoRelatorio.tipo === 'carregando' ? 'gerando...' : 'gerar leitura'}
            </button>
          </div>
        </section>

        {estadoMaquinas.tipo === 'carregando' && (
          <div className="glass-panel animate-pulse rounded-3xl p-6 sm:p-8" aria-label="carregando lista de máquinas">
            <div className="h-4 w-32 rounded-full bg-white/10" />
            <div className="mt-4 h-10 max-w-md rounded-2xl bg-white/10" />
            <div className="mt-8 grid gap-4 sm:grid-cols-3"><div className="h-28 rounded-2xl bg-white/10" /><div className="h-28 rounded-2xl bg-white/10" /><div className="h-28 rounded-2xl bg-white/10" /></div>
          </div>
        )}

        {estadoMaquinas.tipo === 'erro' && (
          <div className="glass-panel rounded-3xl border-status-critico/30 p-6 text-sm text-status-critico" role="alert">
            <div className="flex items-center gap-3"><FileText aria-hidden="true" size={18} /><p>não consegui carregar a frota. {estadoMaquinas.mensagem}</p></div>
          </div>
        )}

        {estadoMaquinas.tipo === 'vazio' && (
          <div className="glass-panel rounded-3xl p-8 text-center text-sm text-field-text3">
            nenhuma máquina cadastrada para gerar relatórios.
          </div>
        )}

        {estadoMaquinas.tipo === 'sucesso' && estadoRelatorio.tipo === 'erro' && (
          <div className="glass-panel rounded-3xl border-status-critico/30 p-6 text-sm text-status-critico" role="alert">
            não consegui gerar esta leitura. {estadoRelatorio.mensagem}
          </div>
        )}

        {estadoMaquinas.tipo === 'sucesso' && estadoRelatorio.tipo === 'vazio' && (
          <div className="glass-panel rounded-3xl p-8 sm:p-12">
            <div className="mx-auto max-w-xl text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-3xl bg-accent/10 text-accent"><FileText aria-hidden="true" size={23} /></div>
              <p className="mt-5 text-lg font-semibold text-field-text1">o relatório ainda está em branco</p>
              <p className="mt-2 text-sm leading-relaxed text-field-text3">Selecione uma máquina, escolha a janela de análise e gere o consolidado. O botão não morde, prometo.</p>
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
            {exportState === 'error' && <p className="mt-3 text-center text-xs text-status-critico" role="alert">não foi possível preparar o arquivo xlsx agora. confira a conexão com a API e tente novamente.</p>}
          </>
        )}
      </div>
    </main>
  );
}

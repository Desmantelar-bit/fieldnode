'use client';

import Link from 'next/link';
import { useState, useEffect, useCallback } from 'react';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { LoadingState } from '@/components/ui/FeedbackStates';
import { HistoryChart } from '@/components/HistoryChart';
import { MetricCard } from '@/components/MetricCard';
import { riskTone, StatusBadge } from '@/components/StatusBadge';
import { PrescricaoModal } from '@/components/PrescricaoModal';
import { telemetryService } from '@/services/telemetryService';
import { ReportButton } from '@/components/ReportButton';
import type { EstadoRequisicao } from '@/types/api';
import type { Telemetry } from '@/types/telemetry';

export default function DetailsPage({ searchParams }: { searchParams: Promise<{ id?: string }> }) {
  const [machineId, setMachineId] = useState<string | null>(null);
  const [estado, setEstado] = useState<EstadoRequisicao<Telemetry[]>>({ tipo: 'carregando' });
  const [showPrescricao, setShowPrescricao] = useState(false);

  const carregar = useCallback((id: string) => {
    setEstado({ tipo: 'carregando' });
    telemetryService.getMachineReadings(id)
      .then((data) =>
        setEstado(data.length === 0 ? { tipo: 'vazio' } : { tipo: 'sucesso', dados: data })
      )
      .catch((err: unknown) =>
        setEstado({ tipo: 'erro', mensagem: err instanceof Error ? err.message : 'API de telemetria nao respondeu' })
      );
  }, []);

  useEffect(() => {
    searchParams.then((params) => {
      const id = params.id ?? null;
      setMachineId(id);
      if (!id) { setEstado({ tipo: 'vazio' }); return; }
      carregar(id);
    });
  }, [searchParams, carregar]);

  if (estado.tipo === 'carregando') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title="Carregando...">
        <LoadingState mensagem="Carregando historico da maquina..." />
      </AppShell>
    );
  }

  if (!machineId) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title="Maquina nao selecionada">
        <EmptyState title="Nenhuma maquina selecionada." message="Volte para maquinas e escolha uma leitura. Sem ID, ate o dashboard fica olhando para o nada." />
      </AppShell>
    );
  }

  if (estado.tipo === 'erro') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title={`Maquina ${machineId}`}>
        <ErrorState title="Nao consegui carregar o historico." message={estado.mensagem} />
      </AppShell>
    );
  }

  if (estado.tipo === 'vazio') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title={`Maquina ${machineId}`}>
        <EmptyState title="Nenhuma leitura encontrada." message="Esta maquina existe no link, mas ainda nao tem telemetria registrada." />
      </AppShell>
    );
  }

  const readings = estado.dados;
  const latest = readings[0];
  const risk = latest.status_risco?.rotuloRisco;
  const tempTone = latest.temperatura > 85 ? 'red' : latest.temperatura > 75 ? 'amber' : 'emerald';
  const vibTone = latest.vibracao > 0.8 ? 'red' : latest.vibracao > 0.5 ? 'amber' : 'emerald';
  const rpmTone = latest.rpm < 1300 ? 'amber' : 'emerald';

  return (
    <>
      <AppShell
        active="/colheitadeiras"
        eyebrow="Detalhes"
        title={`Maquina ${machineId}`}
        actions={
          <div className="flex gap-2">
            <ReportButton machineId={machineId} />
            <button
              onClick={() => setShowPrescricao(true)}
              className="rounded-md border border-blue-500/30 bg-blue-900/20 px-3 py-2 text-sm font-semibold text-blue-200 transition hover:bg-blue-900/40"
            >
              Ver Decisão
            </button>
            <Link href="/colheitadeiras" className="rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]">
              Voltar
            </Link>
          </div>
        }
      >
        <div className="space-y-5">
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Temperatura" value={`${latest.temperatura}C`} tone={tempTone} helper="ultima leitura" />
            <MetricCard label="Vibracao" value={`${latest.vibracao}g`} tone={vibTone} helper="ultima leitura" />
            <MetricCard label="RPM" value={latest.rpm} tone={rpmTone} helper="rotacao atual" />
            <article className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">Status</p>
              <div className="mt-4">
                <StatusBadge tone={riskTone(risk)}>{risk ?? 'Indisponivel'}</StatusBadge>
              </div>
              <p className="mt-4 text-sm text-slate-400">informado pela API</p>
            </article>
          </section>

          <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
            <HistoryChart title="Historico de temperatura" readings={readings} field="temperatura" suffix="C" tone="red" />
            <HistoryChart title="Historico de vibracao" readings={readings} field="vibracao" suffix="g" tone="amber" />
            <HistoryChart title="Historico de RPM" readings={readings} field="rpm" tone="emerald" />
          </section>
        </div>
      </AppShell>

      <PrescricaoModal
        machineId={machineId}
        isOpen={showPrescricao}
        onClose={() => setShowPrescricao(false)}
      />
    </>
  );
}

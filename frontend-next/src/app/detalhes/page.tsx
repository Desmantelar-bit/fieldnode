'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { HistoryChart } from '@/components/HistoryChart';
import { MetricCard } from '@/components/MetricCard';
import { riskTone, StatusBadge } from '@/components/StatusBadge';
import { PrescricaoModal } from '@/components/PrescricaoModal';
import { telemetryService } from '@/services/telemetryService';
import type { Telemetry } from '@/types/telemetry';

function classifyRisk(latest: { temperatura: number; vibracao: number }) {
  if (latest.temperatura > 85 || latest.vibracao > 0.8) return 'CRITICO';
  if (latest.temperatura > 75 || latest.vibracao > 0.5) return 'ATENCAO';
  return 'NORMAL';
}

export default function DetailsPage({ searchParams }: { searchParams: Promise<{ id?: string }> }) {
  const [machineId, setMachineId] = useState<string | null>(null);
  const [readings, setReadings] = useState<Telemetry[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPrescricao, setShowPrescricao] = useState(false);

  useEffect(() => {
    searchParams.then(params => {
      const id = params.id;
      setMachineId(id || null);
      
      if (!id) {
        setLoading(false);
        return;
      }

      telemetryService.getMachineReadings(id)
        .then(setReadings)
        .catch(() => setError('API de telemetria não respondeu'))
        .finally(() => setLoading(false));
    });
  }, [searchParams]);

  if (loading) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title="Carregando...">
        <div className="text-center py-8 text-slate-400">Carregando detalhes da máquina...</div>
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

  if (error) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title={`Maquina ${machineId}`}>
        <ErrorState title="Nao consegui carregar o historico." message="A API de telemetria nao respondeu para esta maquina. Confira o backend e tente novamente." />
      </AppShell>
    );
  }

  if (!readings || readings.length === 0) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title={`Maquina ${machineId}`}>
        <EmptyState title="Nenhuma leitura encontrada." message="Esta maquina existe no link, mas ainda nao tem telemetria registrada." />
      </AppShell>
    );
  }

  const latest = readings[0];
  const riscoObj = latest.status_risco || {};
  const risk = riscoObj.rotuloRisco || classifyRisk(latest);
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
                <StatusBadge tone={riskTone(risk)}>{risk}</StatusBadge>
              </div>
              <p className="mt-4 text-sm text-slate-400">calculado por limites operacionais</p>
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

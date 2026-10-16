'use client';

import Link from 'next/link';
import { useState, useEffect, useCallback } from 'react';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { LoadingState } from '@/components/ui/FeedbackStates';
import { HistoryChart } from '@/components/HistoryChart';
import { MetricColumnChart } from '@/components/MetricColumnChart';
import { MetricCard } from '@/components/MetricCard';
import { METRIC_META, METRIC_ORDER } from '@/lib/metrics';
import type { MetricKey } from '@/lib/metricThresholds';
import { riskTone, StatusBadge } from '@/components/StatusBadge';
import { PrescricaoModal } from '@/components/PrescricaoModal';
import { telemetryService } from '@/services/telemetryService';
import { ReportButton } from '@/components/ReportButton';
import type { EstadoRequisicao } from '@/types/api';
import type { Telemetry } from '@/types/telemetry';

/** Tom do card de linha por métrica — o mesmo vocabulário de risco que a API usa. */
const CHART_TONE: Record<MetricKey, 'red' | 'amber' | 'emerald'> = {
  temperatura: 'red',
  vibracao: 'amber',
  rpm: 'emerald',
};

export default function DetailsPage({ searchParams }: { searchParams: Promise<{ id?: string }> }) {
  const [machineId, setMachineId]       = useState<string | null>(null);
  const [estado, setEstado]             = useState<EstadoRequisicao<Telemetry[]>>({ tipo: 'carregando' });
  const [showPrescricao, setShowPrescricao] = useState(false);
  const [atualizadoEm, setAtualizadoEm] = useState<Date | null>(null);
  const [falhaAtualizacao, setFalhaAtualizacao] = useState(false);

  const carregar = useCallback((id: string, silencioso = false) => {
    if (!silencioso) setEstado({ tipo: 'carregando' });
    return telemetryService.getMachineReadings(id)
      .then((data) => {
        setEstado(data.length === 0 ? { tipo: 'vazio' } : { tipo: 'sucesso', dados: data });
        setAtualizadoEm(new Date());
        setFalhaAtualizacao(false);
      })
      .catch((err: unknown) => {
        if (silencioso) {
          setFalhaAtualizacao(true);
          setEstado((anterior) => anterior.tipo === 'sucesso'
            ? anterior
            : { tipo: 'erro', mensagem: err instanceof Error ? err.message : 'API de telemetria não respondeu' });
          return;
        }
        setEstado({ tipo: 'erro', mensagem: err instanceof Error ? err.message : 'API de telemetria não respondeu' });
      });
  }, []);

  useEffect(() => {
    let active = true;
    searchParams.then((params) => {
      if (!active) return;
      const id = params.id ?? null;
      setMachineId(id);
    });
    return () => {
      active = false;
    };
  }, [searchParams]);

  useEffect(() => {
    if (!machineId) {
      setEstado({ tipo: 'vazio' });
      return;
    }
    let active = true;
    let timeout: number | undefined;
    const scheduleNext = () => {
      timeout = window.setTimeout(() => {
        void carregar(machineId, true).then(() => {
          if (active) scheduleNext();
        });
      }, 5000);
    };
    void carregar(machineId).then(() => {
      if (active) scheduleNext();
    });
    return () => {
      active = false;
      if (timeout !== undefined) window.clearTimeout(timeout);
    };
  }, [machineId, carregar]);

  if (estado.tipo === 'carregando') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title="Carregando...">
        <LoadingState mensagem="Carregando histórico da máquina..." />
      </AppShell>
    );
  }

  if (!machineId) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title="Máquina não selecionada">
        <EmptyState title="nenhuma máquina selecionada." message="selecione uma máquina na listagem para inspecionar seus sensores e histórico operacional." />
      </AppShell>
    );
  }

  if (estado.tipo === 'erro') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title={`Máquina ${machineId}`}>
        <ErrorState title="não conseguimos carregar o histórico." message={estado.mensagem} />
      </AppShell>
    );
  }

  if (estado.tipo === 'vazio') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Detalhes" title={`Máquina ${machineId}`}>
        <EmptyState title="ainda não há sinais por aqui." message="esta máquina ainda não transmitiu pacotes de telemetria para a central." />
      </AppShell>
    );
  }

  const readings = estado.dados;
  const latest   = readings[0];
  const risk     = latest.status_risco?.rotuloRisco;
  const tempTone = latest.temperatura > 85 ? 'red' : latest.temperatura > 75 ? 'amber' : 'emerald';
  const vibTone  = latest.vibracao > 0.8 ? 'red' : latest.vibracao > 0.5 ? 'amber' : 'emerald';
  const rpmTone  = latest.rpm < 1300 ? 'amber' : 'emerald';

  return (
    <>
      <AppShell
        active="/colheitadeiras"
        eyebrow="Detalhes"
        title={`Máquina ${machineId}`}
        actions={
          <div className="flex items-center gap-2">
            <ReportButton machineId={machineId} />
            <button
              type="button"
              onClick={() => setShowPrescricao(true)}
              className="rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] px-3 py-2 text-xs font-semibold text-[var(--text-2)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)] active:scale-95"
            >
              Ver Decisão
            </button>
            <Link
              href="/colheitadeiras"
              className="rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] px-3 py-2 text-xs font-semibold text-[var(--text-2)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)]"
            >
              Voltar
            </Link>
          </div>
        }
      >
        <div className="space-y-5">
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Temperatura" value={`${latest.temperatura}°C`} tone={tempTone} helper="última leitura" />
            <MetricCard label="Vibração"    value={`${latest.vibracao}g`}     tone={vibTone}  helper="última leitura" />
            <MetricCard label="RPM"         value={latest.rpm}                tone={rpmTone}  helper="rotação atual" />
            {/* Mesmo miolo centrado e mesma altura mínima das MetricCard ao
                lado: este card é escrito à mão (carrega um selo, não um número),
                mas precisa alinhar na mesma linha de base dos outros três. */}
            <article className="metric-card flex min-h-[8.75rem] flex-col items-center justify-center text-center transition-all duration-200">
              <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">Status</p>
              <div className="mt-3">
                <StatusBadge tone={riskTone(risk)}>{risk ?? 'Indisponível'}</StatusBadge>
              </div>
              <p className="mt-2 text-xs text-[var(--text-3)]">informado pela API</p>
            </article>
          </section>

          {/* Cada métrica aparece duas vezes, lado a lado e com a MESMA série:
              a linha conta como a grandeza evoluiu; as colunas mostram quais
              leituras ficaram fora da faixa. Dois ângulos, um dado só. */}
          {METRIC_ORDER.map((metric) => {
            const meta = METRIC_META[metric];
            return (
              <section
                key={metric}
                aria-label={`Histórico de ${meta.label}`}
                className="grid grid-cols-1 gap-4 lg:grid-cols-2"
              >
                <HistoryChart
                  title={`Histórico de ${meta.short.toLowerCase()}`}
                  readings={readings}
                  field={metric}
                  suffix={meta.unit}
                  tone={CHART_TONE[metric]}
                />
                <MetricColumnChart
                  title={`Leituras de ${meta.short.toLowerCase()}`}
                  readings={readings}
                  field={metric}
                />
              </section>
            );
          })}
          <p className="text-right text-[11px] text-[var(--text-3)]" role="status">
            {falhaAtualizacao
              ? 'API indisponível; exibindo a última leitura recebida.'
              : 'Atualização automática a cada 5 segundos.'}
            {atualizadoEm && ` Última atualização: ${atualizadoEm.toLocaleTimeString('pt-BR')}.`}
          </p>
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

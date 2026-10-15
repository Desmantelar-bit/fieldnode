'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '@/components/AppShell';
import { ErrorState, EmptyState } from '@/components/EmptyState';
import { LoadingState } from '@/components/ui/FeedbackStates';
import { StatusBadge, riskTone } from '@/components/StatusBadge';
import { telemetryService } from '@/services/telemetryService';
import type { AnalisePrescricao } from '@/types/telemetry';

function sourceLabel(source: string) {
  if (source === 'ia_generativa') return 'Explicação gerada por IA';
  if (source === 'fallback_determinístico') return 'Modo offline: recomendação segura';
  return 'Recomendação determinística';
}

const sourceToneClass = {
  NORMAL: 'border-[color:var(--status-normal)]/20 bg-[color:var(--status-normal)]/8 text-[color:var(--status-normal)]',
  ATENCAO: 'border-[color:var(--status-atencao)]/20 bg-[color:var(--status-atencao)]/8 text-[color:var(--status-atencao)]',
  CRITICO: 'border-[color:var(--status-critico)]/20 bg-[color:var(--status-critico)]/8 text-[color:var(--status-critico)]',
} as const;

type PrescriptionState =
  | { status: 'loading' }
  | { status: 'success'; data: AnalisePrescricao }
  | { status: 'error'; message: string };

export default function PrescricaoPage() {
  const params = useParams<{ id: string }>();
  const maquinaId = params?.id ?? '';
  const [state, setState] = useState<PrescriptionState>({ status: 'loading' });

  useEffect(() => {
    let active = true;
    setState({ status: 'loading' });
    telemetryService.getAnalisePrescricao(maquinaId).then((data) => {
      if (active) setState({ status: 'success', data });
    }).catch((error: unknown) => {
      if (active) {
        setState({
          status: 'error',
          message: error instanceof Error ? error.message : 'Erro desconhecido',
        });
      }
    });
    return () => { active = false; };
  }, [maquinaId]);

  if (!maquinaId) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
        <EmptyState title="Selecione uma máquina." message="Selecione uma máquina para ver a prescrição." />
      </AppShell>
    );
  }

  if (state.status === 'loading') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
        <LoadingState mensagem="Carregando recomendação..." />
      </AppShell>
    );
  }

  if (state.status === 'error') {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
        <ErrorState title="Não consegui carregar a prescrição." message={`${state.message} — tente novamente.`} />
      </AppShell>
    );
  }

  const analise = state.data;
  const texto = analise.explicacao_operador || analise.recomendacao_tecnica || 'Nenhuma ação necessária.';

  return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
        <div className="space-y-5">
          <div>
            <h2 className="text-xl font-bold text-[var(--text-1)]">
              Prescrição para {maquinaId}
            </h2>
            <p className="mt-1 text-sm text-[var(--text-3)]">
              Recomendação operacional baseada na telemetria atual.
            </p>
          </div>

          <section className="metric-card border border-[var(--line)]">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <StatusBadge tone={riskTone(analise.status)}>
                {analise.status}
              </StatusBadge>
              <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-semibold ${sourceToneClass[analise.status]}`}>
                {sourceLabel(analise.fonte_explicacao)}
              </span>
            </div>

            <p className="mt-4 text-sm font-medium leading-relaxed text-[var(--text-1)]">
              {texto}
            </p>

            {analise.recomendacao_tecnica && (
              <p className="mt-3 text-xs text-[var(--text-2)]">
                Conduta técnica: {analise.recomendacao_tecnica}
              </p>
            )}

            {analise.motivos.length > 0 && (
              <p className="mt-2 text-xs text-[var(--text-3)]">
                Motivos: {analise.motivos.join('; ')}.
              </p>
            )}
          </section>
        </div>
      </AppShell>
  );
}

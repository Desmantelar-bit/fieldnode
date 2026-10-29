"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { StatusBadge, riskTone } from '@/components/StatusBadge';
import { telemetryService } from '@/services/telemetryService';
import type { AnalisePrescricao } from '@/types/telemetry';

function sourceLabel(source: AnalisePrescricao['fonte_explicacao']) {
  if (source === 'ia_generativa') return 'Explicação gerada por IA';
  if (source === 'fallback_determinístico') return 'Modo offline: recomendação segura';
  return 'Recomendação determinística';
}

const sourceToneClass = {
  NORMAL: 'border-[color:var(--status-normal)]/20 bg-[color:var(--status-normal)]/8 text-[color:var(--status-normal)]',
  ATENCAO: 'border-[color:var(--status-atencao)]/20 bg-[color:var(--status-atencao)]/8 text-[color:var(--status-atencao)]',
  CRITICO: 'border-[color:var(--status-critico)]/20 bg-[color:var(--status-critico)]/8 text-[color:var(--status-critico)]',
} as const;

export default function PrescricaoPage() {
  const params = useParams<{ id: string }>();
  const maquinaId = params?.id ?? '';
  const [analise, setAnalise] = useState<AnalisePrescricao | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const explicacao = analise?.explicacao_operador?.trim()
    || analise?.recomendacao_tecnica?.trim()
    || 'Nenhuma ação necessária.';
  const condutaTecnica = analise?.recomendacao_tecnica?.trim();
  const mostrarCondutaTecnica = Boolean(
    condutaTecnica && condutaTecnica !== explicacao,
  );
  const textoVisivel = [
    explicacao,
    ...(mostrarCondutaTecnica && condutaTecnica ? [condutaTecnica] : []),
  ].join(' ').toLocaleLowerCase();
  const mostrarMotivos = Boolean(
    analise?.motivos.length
    && !analise.motivos.every((motivo) => textoVisivel.includes(motivo.toLocaleLowerCase())),
  );

  useEffect(() => {
    let active = true;

    telemetryService.getAnalisePrescricao(maquinaId)
      .then((data) => {
        if (active) setAnalise(data);
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : 'Erro desconhecido');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [maquinaId]);

  return (
    <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
      {!maquinaId ? (
        <EmptyState title="Selecione uma máquina." message="Selecione uma máquina para ver a prescrição." />
      ) : loading ? (
        <div className="metric-card animate-pulse py-12 text-center text-sm text-[var(--text-3)]" role="status">
          Analisando telemetria…
        </div>
      ) : error ? (
        <ErrorState
          title="Não consegui carregar a prescrição."
          message={`${error} — tente novamente.`}
        />
      ) : analise ? (
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
              {explicacao}
            </p>

            {mostrarCondutaTecnica && condutaTecnica && (
              <p className="mt-3 text-xs text-[var(--text-2)]">
                Conduta técnica: {condutaTecnica}
              </p>
            )}

            {mostrarMotivos && (
              <p className="mt-2 text-xs text-[var(--text-3)]">
                Motivos: {analise.motivos.join('; ')}.
              </p>
            )}
          </section>
        </div>
      ) : null}
    </AppShell>
  );
}

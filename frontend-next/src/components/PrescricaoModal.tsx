'use client';

import { useEffect } from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { telemetryService } from '@/services/telemetryService';
import { ErrorState } from '@/components/ui/FeedbackStates';
import type { AnalisePrescricao } from '@/types/telemetry';

interface PrescricaoModalProps {
  machineId?: string;
  isOpen: boolean;
  onClose: () => void;
}

function statusTone(status: AnalisePrescricao['status']) {
  switch (status) {
    case 'CRITICO': return 'bg-red-900/50 text-red-200 border-red-700';
    case 'ATENCAO': return 'bg-amber-900/50 text-amber-200 border-amber-700';
    default: return 'bg-green-900/50 text-green-200 border-green-700';
  }
}

function fonteLabel(fonte: AnalisePrescricao['fonte_explicacao']) {
  if (fonte === 'ia_generativa') return 'Explicação por IA';
  if (fonte === 'fallback_determinístico') return 'Recomendação segura (modo offline)';
  return 'Recomendação determinística';
}

export function PrescricaoModal({ machineId, isOpen, onClose }: PrescricaoModalProps) {
  const { mutate } = useSWRConfig();
  const shouldFetch = isOpen && Boolean(machineId);

  useEffect(() => {
    if (!isOpen) {
      mutate(
        (key) => Array.isArray(key) && key[0] === 'analise-prescricao',
        undefined,
        { revalidate: false },
      );
    }
  }, [isOpen, mutate]);

  const { data: analise, error, isLoading: loading } = useSWR<AnalisePrescricao>(
    shouldFetch && machineId ? ['analise-prescricao', machineId] : null,
    ([, id]: readonly ['analise-prescricao', string]) =>
      telemetryService.getAnalisePrescricao(id),
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
      keepPreviousData: false,
    },
  );

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="glass-panel w-full max-w-lg rounded-lg p-6 max-h-[85vh] flex flex-col"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4 shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-slate-50">Prescrição Operacional</h2>
            {machineId && <p className="text-xs text-slate-500 mt-0.5">{machineId}</p>}
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-lg leading-none" aria-label="Fechar">
            ×
          </button>
        </div>

        <div className="overflow-y-auto flex-1 space-y-3 pr-1">
          {!machineId && (
            <p className="text-center py-8 text-slate-400 text-sm">
              Selecione uma máquina para ver a prescrição.
            </p>
          )}

          {loading && (
            <div className="flex items-center justify-center py-10 gap-2 text-slate-400 text-sm">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-300 border-t-transparent" />
              Analisando telemetria...
            </div>
          )}

          {error && (
            <ErrorState mensagem={error instanceof Error ? error.message : "Falha ao carregar prescrição."} />
          )}

          {analise && !loading && (
            <div className={`rounded-lg border p-4 ${statusTone(analise.status)}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider opacity-70">Recomendação atual</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${statusTone(analise.status)}`}>
                  {analise.status}
                </span>
              </div>
              <p className="text-sm font-semibold leading-relaxed">
                {analise.explicacao_operador || analise.recomendacao_tecnica || 'Nenhuma ação necessária.'}
              </p>
              {analise.recomendacao_tecnica && (
                <p className="text-xs opacity-75 mt-3">Conduta técnica: {analise.recomendacao_tecnica}</p>
              )}
              <p className="text-xs opacity-60 mt-3">
                {fonteLabel(analise.fonte_explicacao)} · {new Date(analise.gerado_em).toLocaleString('pt-BR')}
              </p>
            </div>
          )}
        </div>

        <div className="mt-4 flex justify-end shrink-0">
          <button onClick={onClose} className="rounded-md bg-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-600">
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}

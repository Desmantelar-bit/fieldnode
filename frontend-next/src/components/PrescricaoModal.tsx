'use client';

import { useEffect } from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { telemetryService } from '@/services/telemetryService';
import type { Prescricao } from '@/types/telemetry';

interface PrescricaoModalProps {
  machineId?: string;
  isOpen: boolean;
  onClose: () => void;
}

function statusTone(status: string) {
  switch (status) {
    case 'pendente':  return 'bg-amber-900/50 text-amber-200 border-amber-700';
    case 'concluida': return 'bg-green-900/50 text-green-200 border-green-700';
    case 'cancelada': return 'bg-red-900/50 text-red-200 border-red-700';
    default:          return 'bg-blue-900/50 text-blue-200 border-blue-700';
  }
}

function statusLabel(status: string) {
  switch (status) {
    case 'pendente':  return 'Pendente';
    case 'concluida': return 'Concluída';
    case 'cancelada': return 'Cancelada';
    default:          return status;
  }
}

function isAbortError(error: unknown): boolean {
  return (
    error instanceof DOMException && error.name === 'AbortError'
  ) || (
    typeof error === 'object' &&
    error !== null &&
    'name' in error &&
    (error as { name?: string }).name === 'AbortError'
  );
}

export function PrescricaoModal({ machineId, isOpen, onClose }: PrescricaoModalProps) {
  const { mutate } = useSWRConfig();
  const shouldFetch = isOpen && Boolean(machineId);

  useEffect(() => {
    if (!isOpen) {
      mutate(
        (key) => Array.isArray(key) && key[0] === 'prescricoes',
        undefined,
        { revalidate: false },
      );
    }
  }, [isOpen, mutate]);

  const {
    data: prescricoes,
    error,
    isLoading: loading,
  } = useSWR<Prescricao[]>(
    shouldFetch && machineId ? ['prescricoes', machineId] : null,
    async ([, id]: readonly ['prescricoes', string]) => {
      try {
        return await telemetryService.getPrescricoes(id);
      } catch (error) {
        if (isAbortError(error)) return [];
        throw error;
      }
    },
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
      keepPreviousData: false,
    },
  );

  if (!isOpen) return null;

  const latest = prescricoes?.[0] ?? null;
  const history = prescricoes?.slice(1) ?? [];
  const empty = shouldFetch && !loading && !error && prescricoes?.length === 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="glass-panel w-full max-w-lg rounded-lg p-6 max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4 shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-slate-50">Prescrição Operacional</h2>
            {machineId && (
              <p className="text-xs text-slate-500 mt-0.5">{machineId}</p>
            )}
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200 text-lg leading-none">✕</button>
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
            <p className="text-center py-8 text-red-400 text-sm">
              Falha ao carregar prescrição.
            </p>
          )}

          {empty && (
            <p className="text-center py-8 text-slate-400 text-sm">
              Nenhuma prescrição disponível para esta máquina.
            </p>
          )}

          {latest && !loading && (
            <>
              <div className={`rounded-lg border p-4 ${statusTone(latest.status)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider opacity-70">
                    Recomendação atual
                  </span>
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${statusTone(latest.status)}`}>
                    {statusLabel(latest.status)}
                  </span>
                </div>
                <p className="font-semibold text-sm mb-1">{latest.titulo}</p>
                <p className="text-sm opacity-90 leading-relaxed">{latest.descricao}</p>
                <p className="text-xs opacity-50 mt-3">
                  {new Date(latest.data_geracao).toLocaleString('pt-BR')}
                </p>
              </div>

              {history.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    Histórico ({history.length})
                  </p>
                  <div className="space-y-2">
                    {history.map((p) => (
                      <div
                        key={p.id}
                        className={`rounded-md border px-3 py-2 text-xs ${statusTone(p.status)} opacity-70`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{p.titulo}</span>
                          <span className="opacity-60">{statusLabel(p.status)}</span>
                        </div>
                        <p className="opacity-70 mt-0.5 truncate">{p.descricao}</p>
                        <p className="opacity-40 mt-1">
                          {new Date(p.data_geracao).toLocaleString('pt-BR')}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className="mt-4 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="rounded-md bg-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-600"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}

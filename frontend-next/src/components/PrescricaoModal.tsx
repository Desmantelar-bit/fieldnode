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
    case 'pendente': return 'bg-amber-900/50 text-amber-200 border-amber-700';
    case 'concluida': return 'bg-green-900/50 text-green-200 border-green-700';
    case 'cancelada': return 'bg-red-900/50 text-red-200 border-red-700';
    default: return 'bg-blue-900/50 text-blue-200 border-blue-700';
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
        if (isAbortError(error)) {
          return [];
        }
        throw error;
      }
    },
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
      keepPreviousData: false,
    },
  );

  const prescricao = shouldFetch ? (prescricoes?.[0] ?? null) : null;
  const empty = shouldFetch && prescricoes?.length === 0;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="glass-panel w-full max-w-md rounded-lg p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-50">Prescrição Operacional</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200"
          >
            ✕
          </button>
        </div>

        {!machineId && (
          <div className="text-center py-8 text-slate-400">
            Selecione uma máquina para ver a prescrição.
          </div>
        )}

        {loading && (
          <div className="text-center py-8 text-slate-400">
            Carregando prescrição...
          </div>
        )}

        {error && (
          <div className="text-center py-8 text-red-400">
            Falha ao carregar prescrição
          </div>
        )}

        {empty && !loading && !error && (
          <div className="text-center py-8 text-slate-400">
            Nenhuma prescrição encontrada para esta máquina.
          </div>
        )}

        {prescricao && !loading && (
          <div className="space-y-4">
            <div className={`rounded-lg border p-3 ${statusTone(prescricao.status)}`}>
              <div className="text-xs font-semibold uppercase tracking-wider mb-1">
                {prescricao.titulo} • {prescricao.status}
              </div>
              <div className="font-medium">
                {prescricao.descricao}
              </div>
            </div>

            <div className="text-sm text-slate-400">
              <div className="font-medium mb-2">Gerado em:</div>
              <div>{new Date(prescricao.data_geracao).toLocaleString('pt-BR')}</div>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end">
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

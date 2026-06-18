'use client';

import { useState, useEffect } from 'react';
import { telemetryService } from '@/services/telemetryService';
import type { Prescricao } from '@/types/telemetry';

interface PrescricaoModalProps {
  machineId: string;
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

export function PrescricaoModal({ machineId, isOpen, onClose }: PrescricaoModalProps) {
  const [prescricao, setPrescricao] = useState<Prescricao | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && machineId) {
      setLoading(true);
      setError(null);
      setPrescricao(null);
      telemetryService.getPrescricao(machineId)
        .then(setPrescricao)
        .catch(() => setError('Falha ao carregar prescrição'))
        .finally(() => setLoading(false));
    }
  }, [isOpen, machineId]);

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

        {loading && (
          <div className="text-center py-8 text-slate-400">
            Carregando prescrição...
          </div>
        )}

        {error && (
          <div className="text-center py-8 text-red-400">
            {error}
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

'use client';

import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import useSWR from 'swr';
import { telemetryService } from '@/services/telemetryService';
import { ErrorState } from '@/components/ui/FeedbackStates';
import type { AnalisePrescricao } from '@/types/telemetry';

interface PrescricaoModalProps {
  machineId?: string;
  isOpen: boolean;
  onClose: () => void;
}

function statusStyle(status: AnalisePrescricao['status']) {
  switch (status) {
    case 'CRITICO':
      return 'border-[color:var(--status-critico)]/25 bg-[color:var(--status-critico)]/8 text-[color:var(--status-critico)]';
    case 'ATENCAO':
      return 'border-[color:var(--status-atencao)]/25 bg-[color:var(--status-atencao)]/8 text-[color:var(--status-atencao)]';
    default:
      return 'border-[color:var(--status-normal)]/25 bg-[color:var(--status-normal)]/8 text-[color:var(--status-normal)]';
  }
}

function fonteLabel(fonte: AnalisePrescricao['fonte_explicacao']) {
  if (fonte === 'ia_generativa') return 'Explicação por IA';
  if (fonte === 'fallback_determinístico') return 'Recomendação segura (modo offline)';
  return 'Recomendação determinística';
}

export function PrescricaoModal({ machineId, isOpen, onClose }: PrescricaoModalProps) {
  const [mounted, setMounted] = useState(false);
  const swrKey = isOpen && machineId ? ['analise-prescricao', machineId] as const : null;

  const { data: analise, error } = useSWR<AnalisePrescricao>(
    swrKey,
    ([, id]: readonly ['analise-prescricao', string]) => telemetryService.getAnalisePrescricao(id),
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
      keepPreviousData: false,
    },
  );

  useEffect(() => {
    if (!isOpen) return;
    setMounted(true);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen || !mounted) return null;

  const currentAnalise = machineId && analise?.maquina_id === machineId ? analise : undefined;
  const visibleAnalise = currentAnalise && !error ? currentAnalise : undefined;
  const showData = Boolean(visibleAnalise);
  const showLoading = Boolean(machineId) && !visibleAnalise && !error;

  return createPortal(
    <div
      className="fixed inset-0 z-[120] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="prescricao-title"
        className="liquid-glass--elevated flex max-h-[min(85vh,44rem)] w-full max-w-lg flex-col p-5 shadow-[var(--shadow-elevated)]"
      >
        <div className="mb-4 flex shrink-0 items-center justify-between gap-3">
          <div>
            <h2 id="prescricao-title" className="text-base font-bold text-[var(--text-1)]">Prescrição Operacional</h2>
            {machineId && <p className="mt-0.5 font-mono text-xs text-[var(--text-3)]">{machineId}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar prescrição operacional"
            className="flex h-8 w-8 items-center justify-center rounded-xl bg-[var(--panel-glass-mid)] text-[var(--text-3)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)] active:scale-95"
          >
            <X size={15} aria-hidden="true" />
          </button>
        </div>

        <div className="min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
          {!machineId && <p className="py-8 text-center text-sm text-[var(--text-3)]">Selecione uma máquina para ver a prescrição.</p>}
          {showLoading && (
            <div className="flex items-center justify-center gap-2.5 py-10 text-[var(--text-3)]">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-[color:var(--ui-accent)] border-t-transparent" />
              <span className="text-xs font-semibold uppercase tracking-[0.1em]">Analisando telemetria...</span>
            </div>
          )}
          {error && <ErrorState mensagem={error instanceof Error ? error.message : 'Falha ao carregar prescrição.'} />}
          {showData && visibleAnalise && (
            <div className={`rounded-xl border p-4 ${statusStyle(visibleAnalise.status)}`}>
              <div className="mb-3 flex items-center justify-between gap-2">
                <span className="text-[10px] font-semibold uppercase tracking-[0.1em] opacity-70">Recomendação atual</span>
                <span className={`rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.1em] ${statusStyle(visibleAnalise.status)}`}>{visibleAnalise.status}</span>
              </div>
              <p className="text-sm font-semibold leading-relaxed">{visibleAnalise.explicacao_operador || visibleAnalise.recomendacao_tecnica || 'Nenhuma ação necessária.'}</p>
              {visibleAnalise.recomendacao_tecnica && visibleAnalise.recomendacao_tecnica !== visibleAnalise.explicacao_operador && (
                <p className="mt-3 text-xs opacity-75">Conduta técnica: {visibleAnalise.recomendacao_tecnica}</p>
              )}
              <p className="mt-3 text-[10px] opacity-60">{fonteLabel(visibleAnalise.fonte_explicacao)} · {new Date(visibleAnalise.gerado_em).toLocaleString('pt-BR')}</p>
            </div>
          )}
        </div>

        <div className="mt-4 flex shrink-0 justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl bg-[var(--panel-glass-mid)] px-4 py-2 text-sm font-semibold text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] active:scale-95"
          >
            Fechar
          </button>
        </div>
      </section>
    </div>,
    document.body,
  );
}

'use client';

import { useEffect, useState } from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { ErrorState } from '@/components/ui/FeedbackStates';
import { getStoredAuthToken, telemetryService } from '@/services/telemetryService';
import type { AnalisePrescricao, Decision } from '@/types/telemetry';

interface PrescricaoModalProps { machineId?: string; isOpen: boolean; onClose: () => void; }

function statusTone(status: AnalisePrescricao['status']) {
  if (status === 'CRITICO') return 'bg-red-900/50 text-red-200 border-red-700';
  if (status === 'ATENCAO') return 'bg-amber-900/50 text-amber-200 border-amber-700';
  return 'bg-green-900/50 text-green-200 border-green-700';
}

function decisionStatusTone(status: Decision['status']) {
  if (status === 'APROVADA') return 'border-status-normal/40 bg-status-normal/10 text-status-normal';
  if (status === 'REJEITADA') return 'border-status-critico/40 bg-status-critico/10 text-status-critico';
  if (status === 'EXECUTADA') return 'border-sky-400/40 bg-sky-400/10 text-sky-200';
  if (status === 'EXPIRADA') return 'border-amber-400/40 bg-amber-400/10 text-amber-200';
  return 'border-field-border bg-field-glass text-field-text2';
}

function fonteLabel(fonte: AnalisePrescricao['fonte_explicacao']) {
  if (fonte === 'ia_generativa') return 'Explicação por IA';
  if (fonte === 'fallback_determinístico') return 'Recomendação segura (modo offline)';
  return 'Recomendação determinística';
}

function actionErrorMessage(error: unknown) {
  if ((error instanceof DOMException && error.name === 'AbortError') || error instanceof TypeError) return 'Não foi possível conectar ao servidor. Tente novamente.';
  if (error instanceof Error && error.message.includes('HTTP 400')) return 'Não foi possível atualizar esta decisão. Ela pode ter sido alterada por outra sessão.';
  return 'Não foi possível atualizar esta decisão. Tente novamente.';
}

export function PrescricaoModal({ machineId, isOpen, onClose }: PrescricaoModalProps) {
  const { mutate } = useSWRConfig();
  const [updatedDecision, setUpdatedDecision] = useState<Decision | null>(null);
  const [outcomeTexto, setOutcomeTexto] = useState('');
  const [pendingStatus, setPendingStatus] = useState<Decision['status'] | null>(null);
  const [actionFeedback, setActionFeedback] = useState<{ type: 'error' | 'success'; text: string } | null>(null);
  const shouldFetch = isOpen && Boolean(machineId);

  useEffect(() => {
    if (!isOpen) mutate((key) => Array.isArray(key) && key[0] === 'analise-prescricao', undefined, { revalidate: false });
  }, [isOpen, mutate]);

  useEffect(() => {
    if (!isOpen) {
      setUpdatedDecision(null);
      setOutcomeTexto('');
      setPendingStatus(null);
      setActionFeedback(null);
    }
  }, [isOpen]);

  const { data: analise, error, isLoading: loading } = useSWR<AnalisePrescricao>(
    shouldFetch && machineId ? ['analise-prescricao', machineId] : null,
    ([, id]: readonly ['analise-prescricao', string]) => telemetryService.getAnalisePrescricao(id),
    { revalidateOnFocus: false, revalidateIfStale: false, keepPreviousData: false },
  );

  useEffect(() => {
    setUpdatedDecision(null); setOutcomeTexto(''); setPendingStatus(null); setActionFeedback(null);
  }, [analise?.decision_id, analise?.decision_status]);

  async function atualizarDecisionStatus(status: Decision['status']) {
    const decisionId = analise?.decision_id;
    if (!decisionId) {
      setActionFeedback({ type: 'error', text: 'Esta prescrição não possui uma Decision associada. Ações operacionais indisponíveis para este registro.' });
      return;
    }
    if (!getStoredAuthToken()) {
      const next = `${window.location.pathname}${window.location.search}`;
      window.location.assign(`/login?next=${encodeURIComponent(next)}`);
      return;
    }
    if ((status === 'REJEITADA' && !window.confirm('Tem certeza que deseja rejeitar esta ação?')) || (status === 'EXECUTADA' && !window.confirm('Confirmar que esta ação foi executada?'))) return;

    setPendingStatus(status); setActionFeedback(null);
    try {
      const decision = await telemetryService.updateDecision(decisionId, status, outcomeTexto);
      setUpdatedDecision(decision);
      setActionFeedback({ type: 'success', text: status === 'APROVADA' ? 'Ação aprovada.' : status === 'REJEITADA' ? 'Ação rejeitada.' : 'Ação marcada como executada.' });
    } catch (actionError) {
      setActionFeedback({ type: 'error', text: actionErrorMessage(actionError) });
    } finally { setPendingStatus(null); }
  }

  if (!isOpen) return null;
  const decisionStatus = updatedDecision?.status ?? analise?.decision_status;
  const hasDecision = Boolean(analise?.decision_id && decisionStatus);
  const isPending = decisionStatus === 'PENDENTE';
  const isApproved = decisionStatus === 'APROVADA';
  const isSubmitting = pendingStatus !== null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="glass-panel flex max-h-[85vh] w-full max-w-lg flex-col rounded-lg p-6" onClick={(event) => event.stopPropagation()}>
        <div className="mb-4 flex shrink-0 items-center justify-between"><div><h2 className="text-lg font-semibold text-slate-50">Prescrição Operacional</h2>{machineId && <p className="mt-0.5 text-xs text-slate-500">{machineId}</p>}</div><button onClick={onClose} className="text-lg leading-none text-slate-400 hover:text-slate-200" aria-label="Fechar">×</button></div>
        <div className="flex-1 space-y-3 overflow-y-auto pr-1">
          {!machineId && <p className="py-8 text-center text-sm text-slate-400">Selecione uma máquina para ver a prescrição.</p>}
          {loading && <div className="flex items-center justify-center gap-2 py-10 text-sm text-slate-400"><div className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-300 border-t-transparent" />Analisando telemetria...</div>}
          {error && <ErrorState mensagem={error instanceof Error ? error.message : 'Falha ao carregar prescrição.'} />}
          {analise && !loading && <>
            <div className={`rounded-lg border p-4 ${statusTone(analise.status)}`}><div className="mb-2 flex items-center justify-between"><span className="text-xs font-bold uppercase tracking-wider opacity-70">Recomendação atual</span><span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${statusTone(analise.status)}`}>{analise.status}</span></div><p className="text-sm font-semibold leading-relaxed">{analise.explicacao_operador || analise.recomendacao_tecnica || 'Nenhuma ação necessária.'}</p>{analise.recomendacao_tecnica && <p className="mt-3 text-xs opacity-75">Conduta técnica: {analise.recomendacao_tecnica}</p>}<p className="mt-3 text-xs opacity-60">{fonteLabel(analise.fonte_explicacao)} · {new Date(analise.gerado_em).toLocaleString('pt-BR')}</p></div>
            {!hasDecision || !decisionStatus ? <p className="border border-amber-400/30 bg-amber-400/10 p-3 text-xs leading-5 text-amber-100" role="status">Esta prescrição não possui uma Decision associada. Ações operacionais indisponíveis para este registro legado.</p> : <section className="border border-field-border bg-field-glass p-4" aria-label="Ações da decisão"><div className="flex items-center justify-between gap-3"><p className="text-xs font-semibold uppercase tracking-label text-field-text3">Status da decisão</p><span className={`border px-2 py-1 text-xs font-semibold ${decisionStatusTone(decisionStatus)}`}>{decisionStatus}</span></div>{(isPending || isApproved) && <label className="mt-4 block text-xs font-semibold text-field-text3" htmlFor="decision-outcome">Observação opcional<textarea id="decision-outcome" className="mt-2 min-h-20 w-full resize-y border border-field-border bg-field-glass p-2 text-sm text-field-text1 outline-none focus:border-status-normal focus:ring-2 focus:ring-[var(--focus-ring)] disabled:opacity-60" disabled={isSubmitting} maxLength={1000} onChange={(event) => setOutcomeTexto(event.target.value)} placeholder={isPending ? 'Motivo da rejeição, se necessário' : 'Resultado observado, se necessário'} value={outcomeTexto} /></label>}<div className="mt-4 flex flex-wrap gap-2">{isPending && <><button className="min-h-11 bg-status-normal px-4 py-2 text-sm font-semibold text-lime-950 transition hover:bg-lime-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-status-normal disabled:cursor-not-allowed disabled:opacity-60" disabled={isSubmitting} onClick={() => atualizarDecisionStatus('APROVADA')} type="button">{pendingStatus === 'APROVADA' ? 'Aprovando...' : 'Aprovar ação'}</button><button className="min-h-11 border border-status-critico/60 px-4 py-2 text-sm font-semibold text-status-critico transition hover:bg-status-critico/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-status-critico disabled:cursor-not-allowed disabled:opacity-60" disabled={isSubmitting} onClick={() => atualizarDecisionStatus('REJEITADA')} type="button">{pendingStatus === 'REJEITADA' ? 'Rejeitando...' : 'Rejeitar'}</button></>}{isApproved && <button className="min-h-11 bg-sky-300 px-4 py-2 text-sm font-semibold text-sky-950 transition hover:bg-sky-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300 disabled:cursor-not-allowed disabled:opacity-60" disabled={isSubmitting} onClick={() => atualizarDecisionStatus('EXECUTADA')} type="button">{pendingStatus === 'EXECUTADA' ? 'Registrando...' : 'Marcar como executada'}</button>}</div>{updatedDecision?.outcome_texto && <p className="mt-3 text-xs leading-5 text-field-text3">Observação registrada: {updatedDecision.outcome_texto}</p>}</section>}
            {actionFeedback && <p className={`border p-3 text-sm ${actionFeedback.type === 'success' ? 'border-status-normal/35 bg-status-normal/10 text-field-text1' : 'border-status-critico/35 bg-status-critico/10 text-field-text1'}`} role={actionFeedback.type === 'error' ? 'alert' : 'status'}>{actionFeedback.text}</p>}
          </>}
        </div>
        <div className="mt-4 flex shrink-0 justify-end"><button onClick={onClose} className="rounded-md bg-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-600">Fechar</button></div>
      </div>
    </div>
  );
}

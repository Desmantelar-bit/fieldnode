'use client';

import { useCallback, useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { LoadingState } from '@/components/ui/FeedbackStates';
import { decisionService } from '@/services/decisionService';
import { DecisaoSchema, type Decisao } from '@/schemas/decisoes';

const statusLabel: Record<string, string> = {
  PENDENTE: 'Pendente', APROVADA: 'Aprovada', REJEITADA: 'Rejeitada',
  EXECUTADA: 'Executada', EXPIRADA: 'Expirada',
};
const actionLabel: Record<string, string> = {
  APROVADA: 'Aprovar', REJEITADA: 'Rejeitar', EXECUTADA: 'Marcar executada', EXPIRADA: 'Expirar',
};

export default function DecisoesPage() {
  const [items, setItems] = useState<Decisao[]>([]);
  const [selected, setSelected] = useState<Decisao | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [outcome, setOutcome] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await decisionService.list({ page_size: 100 });
      setItems(result.results);
      setSelected((current) => current ? result.results.find((d) => d.id === current.id) ?? null : null);
      setError('');
    } catch (err) { setError(err instanceof Error ? err.message : 'Falha ao carregar decisões.'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const openDecision = async (decision: Decisao) => {
    setSelected(decision);
    setOutcome(decision.outcome_texto ?? '');
    try {
      const response = await fetch(`/api/decisions/${decision.id}/`, { headers: { Accept: 'application/json' }, cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setSelected(DecisaoSchema.parse(await response.json()));
    } catch { setError('Não foi possível carregar o detalhe desta decisão.'); }
  };

  const changeStatus = async (next: string) => {
    if (!selected) return;
    const previous = selected;
    const optimistic = { ...selected, status: next as Decisao['status'], outcome_texto: outcome || selected.outcome_texto };
    setSelected(optimistic);
    setItems((current) => current.map((item) => item.id === optimistic.id ? optimistic : item));
    setSaving(true); setError('');
    try {
      const saved = await decisionService.update(selected.id, next, outcome || undefined);
      setSelected(saved);
      setItems((current) => current.map((item) => item.id === saved.id ? saved : item));
      setOutcome(saved.outcome_texto ?? '');
    } catch (err) {
      setSelected(previous);
      setItems((current) => current.map((item) => item.id === previous.id ? previous : item));
      setError(err instanceof Error ? err.message : 'A ação não foi registrada.');
    } finally { setSaving(false); }
  };

  return <AppShell active="/decisoes" eyebrow="FieldNode / Operação" title="Central de decisões" description="Recomendações, evidências e ações registradas pela operação.">
    {loading ? <LoadingState mensagem="Carregando decisões..." /> : error && !items.length ? <ErrorState title="Central indisponível" message={error} /> : !items.length ? <EmptyState title="Fila vazia" message="Não há decisões para as máquinas disponíveis." /> :
      <div className="grid gap-5 lg:grid-cols-[minmax(18rem,0.8fr)_minmax(0,1.4fr)]">
        <section aria-label="Fila de decisões" className="space-y-3">
          <h2 className="section-heading">Fila · {items.length}</h2>
          {items.map((decision) => <button key={decision.id} type="button" onClick={() => void openDecision(decision)} className={`metric-card w-full p-4 text-left ${selected?.id === decision.id ? 'border-[color:var(--ui-accent)]' : ''}`}>
            <span className="flex items-center justify-between gap-2"><span className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-3)]">{decision.severidade}</span><span className="text-xs text-[var(--text-2)]">{statusLabel[decision.status]}</span></span>
            <span className="mt-2 block font-semibold text-[var(--text-1)]">{decision.machine_external_code}</span>
            <span className="mt-1 block line-clamp-2 text-sm text-[var(--text-2)]">{decision.texto}</span>
          </button>)}
        </section>
        <section aria-label="Detalhe da decisão" className="liquid-glass min-w-0 p-5">
          {!selected ? <p className="py-12 text-center text-sm text-[var(--text-3)]">Selecione uma recomendação para consultar evidências e ações.</p> : <>
            <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="section-heading">{selected.machine_external_code} · {selected.severidade}</p><h2 className="mt-1 text-lg font-semibold text-[var(--text-1)]">{selected.texto}</h2></div><span className="status-pill px-3 py-1.5 text-xs">{statusLabel[selected.status]}</span></div>
            <p className="mt-4 text-sm leading-relaxed text-[var(--text-2)]"><strong className="text-[var(--text-1)]">Ação recomendada:</strong> {selected.acao_recomendada}</p>
            <div className="mt-4 rounded-xl border border-[var(--line)] p-4"><h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">Evidência observada</h3>
              {selected.evidencia?.leitura ? <dl className="mt-3 grid grid-cols-2 gap-3 text-sm"><div><dt className="text-xs text-[var(--text-3)]">Temperatura</dt><dd>{selected.evidencia.leitura.temperatura} °C</dd></div><div><dt className="text-xs text-[var(--text-3)]">Vibração</dt><dd>{selected.evidencia.leitura.vibracao}</dd></div><div><dt className="text-xs text-[var(--text-3)]">RPM</dt><dd>{selected.evidencia.leitura.rpm}</dd></div><div><dt className="text-xs text-[var(--text-3)]">Qualidade</dt><dd>{selected.evidencia.evento.evidence_quality}{selected.evidencia.evento.needs_verification ? ' · requer verificação' : ''}</dd></div><div className="col-span-2"><dt className="text-xs text-[var(--text-3)]">Event time / origem</dt><dd>{selected.evidencia.leitura.event_time ? new Date(selected.evidencia.leitura.event_time).toLocaleString('pt-BR') : 'Horário indisponível'} · {selected.evidencia.leitura.time_source}</dd></div></dl> : <p className="mt-2 text-sm text-[var(--text-3)]">Evidência de leitura não vinculada a esta recomendação.</p>}
            </div>
            <label className="mt-4 block text-xs font-semibold text-[var(--text-2)]">Resultado informado pelo operador<textarea value={outcome} onChange={(e) => setOutcome(e.target.value)} maxLength={5000} rows={3} className="mt-2 w-full rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-3 text-sm text-[var(--text-1)]" placeholder="Descreva o resultado observado após a ação." /></label>
            {error && <p role="alert" className="mt-3 text-sm text-[color:var(--status-critico)]">{error}</p>}
            <div className="mt-4 flex flex-wrap gap-2">{selected.transicoes_permitidas.map((status) => <button key={status} type="button" disabled={saving} onClick={() => void changeStatus(status)} className="btn-brand min-h-10 rounded-xl px-4 text-xs font-bold disabled:opacity-50">{saving ? 'Salvando...' : actionLabel[status] ?? statusLabel[status]}</button>)}</div>
            <section className="mt-6 border-t border-[var(--line)] pt-4"><h3 className="section-heading">Linha do tempo</h3>{selected.historico?.length ? <ol className="mt-3 space-y-3">{selected.historico.map((item, index) => <li key={`${item.quando}-${index}`} className="border-l-2 border-[color:var(--ui-accent)]/40 pl-3 text-sm"><p className="font-semibold text-[var(--text-1)]">{{'decision.approve':'Aprovada','decision.reject':'Rejeitada','decision.execute':'Execução registrada','decision.expirada':'Expirada'}[item.action] ?? item.action}</p><p className="text-xs text-[var(--text-3)]">{item.ator ?? 'Sistema'} · {new Date(item.quando).toLocaleString('pt-BR')}</p></li>)}</ol> : <p className="mt-2 text-sm text-[var(--text-3)]">Nenhuma movimentação registrada.</p>}</section>
          </>}
        </section>
      </div>}
  </AppShell>;
}

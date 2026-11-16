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
  const [exportData, setExportData] = useState<{ mensagem: string; whatsapp_url: string | null } | null>(null);
  const [copied, setCopied] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('FALSO_ALARME');
  const [overrideMetric, setOverrideMetric] = useState('temperatura');
  const [overrideAttention, setOverrideAttention] = useState('80');
  const [overrideCritical, setOverrideCritical] = useState('85');
  const [overrideExpiry, setOverrideExpiry] = useState(() => new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 16));
  const [overrideReason, setOverrideReason] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const result = await decisionService.list({ page_size: 100 });
      setItems(result.results);
      const requestedId = new URLSearchParams(window.location.search).get('decision');
      const requested = requestedId ? result.results.find((d) => d.id === requestedId) : undefined;
      const selectedFromList = requested;
      const selectedId = selectedFromList?.id ?? requestedId;
      setSelected(selectedFromList ?? null);
      if (selectedId) {
        setOutcome(selectedFromList?.outcome_texto ?? '');
        const detailResponse = await fetch(`/api/decisions/${selectedId}/`, { headers: { Accept: 'application/json' }, cache: 'no-store' });
        if (detailResponse.ok) {
          const detail = DecisaoSchema.parse(await detailResponse.json());
          setSelected(detail);
          setOutcome(detail.outcome_texto ?? '');
        }
      }
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
      setExportData(null);
    } catch { setError('Não foi possível carregar o detalhe desta decisão.'); }
  };

  const loadExport = async () => {
    if (!selected?.work_order) return;
    const response = await fetch(`/api/workorders/${selected.work_order.id}/export.json`, { headers: { Accept: 'application/json' }, cache: 'no-store' });
    if (!response.ok) throw new Error('Não foi possível preparar a mensagem da OS.');
    setExportData(await response.json() as { mensagem: string; whatsapp_url: string | null });
  };

  const changeStatus = async (next: string) => {
    if (!selected) return;
    const previous = selected;
    const optimistic = { ...selected, status: next as Decisao['status'], outcome_texto: outcome || selected.outcome_texto };
    setSelected(optimistic);
    setItems((current) => current.map((item) => item.id === optimistic.id ? optimistic : item));
    setSaving(true); setError('');
    try {
      const saved = await decisionService.update(selected.id, next, outcome || undefined, next === 'REJEITADA' ? rejectionReason : undefined);
      setSelected(saved);
      setItems((current) => current.map((item) => item.id === saved.id ? saved : item));
      setOutcome(saved.outcome_texto ?? '');
    } catch (err) {
      setSelected(previous);
      setItems((current) => current.map((item) => item.id === previous.id ? previous : item));
      setError(err instanceof Error ? err.message : 'A ação não foi registrada.');
    } finally { setSaving(false); }
  };

  const createOverride = async () => {
    if (!selected) return;
    setSaving(true); setError('');
    try {
      const response = await fetch(`/api/decisions/${selected.id}/threshold-override/`, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-FieldNode-CSRF': '1' }, body: JSON.stringify({ metric: overrideMetric, atencao: Number(overrideAttention), critico: Number(overrideCritical), motivo: overrideReason, expira_em: new Date(overrideExpiry).toISOString() }) });
      if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detalhe || `HTTP ${response.status}`); }
      setOverrideReason('');
      setError('Limiar temporário registrado e auditado.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Não foi possível registrar o override.'); }
    finally { setSaving(false); }
  };

  return <AppShell active="/decisoes" eyebrow="FieldNode / Operação" title="Central de decisões" description="Recomendações, evidências e ações registradas pela operação.">
    {selected?.contexto_maquina && <section className="mb-4 rounded-xl border border-[var(--line)] p-4" aria-label="Contexto da máquina"><h2 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">Contexto da máquina</h2><p className="mt-2 text-sm text-[var(--text-2)]">{selected.contexto_maquina.modelo || 'Modelo não informado'}{selected.contexto_maquina.ano ? ' · ' + selected.contexto_maquina.ano : ''} · Horas acumuladas: {selected.contexto_maquina.horas_motor ?? 'indisponíveis'} · Horas desde a última manutenção: {selected.contexto_maquina.horas_desde_ultima_manutencao ?? 'indisponíveis'}</p></section>}
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
        <section data-testid="decision-detail" aria-label="Detalhe da decisão" className="liquid-glass min-w-0 p-5">
          {!selected ? <p className="py-12 text-center text-sm text-[var(--text-3)]">Selecione uma recomendação para consultar evidências e ações.</p> : <>
            <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="section-heading">{selected.machine_external_code} · {selected.severidade}</p><h2 className="mt-1 text-lg font-semibold text-[var(--text-1)]">{selected.texto}</h2></div><span data-testid="decision-status" className="status-pill px-3 py-1.5 text-xs">{statusLabel[selected.status]}</span></div>
            <p className="mt-4 text-sm leading-relaxed text-[var(--text-2)]"><strong className="text-[var(--text-1)]">Ação recomendada:</strong> {selected.acao_recomendada}</p>
            <div className="mt-4 rounded-xl border border-[var(--line)] p-4"><h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">Evidência observada</h3>
              {selected.evidencia?.leitura ? <dl className="mt-3 grid grid-cols-2 gap-3 text-sm"><div><dt className="text-xs text-[var(--text-3)]">Temperatura</dt><dd>{selected.evidencia.leitura.temperatura} °C</dd></div><div><dt className="text-xs text-[var(--text-3)]">Vibração</dt><dd>{selected.evidencia.leitura.vibracao}</dd></div><div><dt className="text-xs text-[var(--text-3)]">RPM</dt><dd>{selected.evidencia.leitura.rpm}</dd></div><div><dt className="text-xs text-[var(--text-3)]">Qualidade</dt><dd>{selected.evidencia.evento.evidence_quality}{selected.evidencia.evento.needs_verification ? ' · requer verificação' : ''}</dd></div><div className="col-span-2"><dt className="text-xs text-[var(--text-3)]">Event time / origem</dt><dd>{selected.evidencia.leitura.event_time ? new Date(selected.evidencia.leitura.event_time).toLocaleString('pt-BR') : 'Horário indisponível'} · {selected.evidencia.leitura.time_source}</dd></div></dl> : <p className="mt-2 text-sm text-[var(--text-3)]">Evidência de leitura não vinculada a esta recomendação.</p>}
            </div>
            <label className="mt-4 block text-xs font-semibold text-[var(--text-2)]">Resultado informado pelo operador<textarea data-testid="decision-outcome" value={outcome} onChange={(e) => setOutcome(e.target.value)} maxLength={5000} rows={3} className="mt-2 w-full rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-3 text-sm text-[var(--text-1)]" placeholder="Descreva o resultado observado após a ação." /></label>
            {selected.status === 'PENDENTE' && <label className="mt-4 block text-xs font-semibold text-[var(--text-2)]">Motivo da rejeição<select value={rejectionReason} onChange={(e) => setRejectionReason(e.target.value)} className="mt-2 w-full rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-3 text-sm"><option value="FALSO_ALARME">Falso alarme</option><option value="OUTRO">Outro motivo</option></select></label>}
            {selected.status === 'REJEITADA' && selected.motivo_rejeicao === 'FALSO_ALARME' && <section className="mt-4 rounded-xl border border-[var(--line)] p-4" aria-label="Ajustar limiar da máquina"><h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">Ajustar limiar desta máquina</h3><p className="mt-2 text-xs text-[var(--text-3)]">O teto crítico do contrato continua valendo. O ajuste expira automaticamente.</p><div className="mt-3 grid gap-2 sm:grid-cols-2"><label className="text-xs">Métrica<select value={overrideMetric} onChange={(e) => setOverrideMetric(e.target.value)} className="mt-1 w-full rounded-lg border border-[var(--line)] p-2"><option value="temperatura">Temperatura</option><option value="vibracao">Vibração</option></select></label><label className="text-xs">Expira em<input type="datetime-local" value={overrideExpiry} onChange={(e) => setOverrideExpiry(e.target.value)} className="mt-1 w-full rounded-lg border border-[var(--line)] p-2" /></label><label className="text-xs">Atenção<input type="number" value={overrideAttention} onChange={(e) => setOverrideAttention(e.target.value)} className="mt-1 w-full rounded-lg border border-[var(--line)] p-2" /></label><label className="text-xs">Crítico<input type="number" value={overrideCritical} onChange={(e) => setOverrideCritical(e.target.value)} className="mt-1 w-full rounded-lg border border-[var(--line)] p-2" /></label></div><textarea value={overrideReason} onChange={(e) => setOverrideReason(e.target.value)} className="mt-3 w-full rounded-lg border border-[var(--line)] p-2 text-sm" placeholder="Justificativa operacional obrigatória" /><button type="button" disabled={saving || !overrideReason.trim()} onClick={() => void createOverride()} className="btn-brand mt-3 min-h-10 rounded-xl px-4 text-xs font-bold">Registrar ajuste auditado</button></section>}
            <section className="mt-4 rounded-xl border border-[var(--line)] p-4" aria-label="Saídas da ordem de serviço">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">Levar a OS para o trabalho</h3>
              {selected.work_order ? <div className="mt-3 flex flex-wrap gap-2"><a className="btn-brand inline-flex min-h-10 items-center rounded-xl px-4 text-xs font-bold" href={`/api/workorders/${selected.work_order.id}/export.ics`}>Baixar .ics</a><button type="button" className="min-h-10 rounded-xl border border-[var(--line)] px-4 text-xs font-bold" onClick={() => void loadExport()}>Preparar mensagem</button>{exportData && <><button type="button" className="min-h-10 rounded-xl border border-[var(--line)] px-4 text-xs font-bold" onClick={() => { void navigator.clipboard.writeText(exportData.mensagem); setCopied(true); }}>Copiar mensagem</button>{exportData.whatsapp_url && <a className="min-h-10 rounded-xl border border-[var(--line)] px-4 py-2 text-xs font-bold" href={exportData.whatsapp_url} target="_blank" rel="noreferrer">Abrir WhatsApp</a>}<p className="basis-full text-xs text-[var(--text-3)]">{copied ? 'Mensagem copiada.' : 'O link abre o WhatsApp com o texto preenchido. Nada é enviado pelo FieldNode.'}</p></>}</div> : <p className="mt-2 text-sm text-[var(--text-3)]">A OS ainda não foi criada para esta decisão.</p>}
            </section>
            <section className="mt-4 rounded-xl border border-[var(--line)] p-4"><h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">Resultado informado</h3><p className="mt-2 text-sm text-[var(--text-2)]">Relato registrado pelo responsável: {selected.outcome_texto || 'Ainda não informado.'}</p></section>
            <section className="mt-4 rounded-xl border border-[var(--line)] p-4"><h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">Verificado por telemetria</h3><p className="mt-2 text-sm text-[var(--text-2)]">{selected.work_order?.reevaluation ? ({ 'SINTOMA_CESSOU': 'O sintoma não foi observado nas leituras válidas analisadas.', 'SINTOMA_PERSISTE': 'O sintoma continua presente nas leituras analisadas.', 'DADOS_INSUFICIENTES': 'Não há dados suficientes para verificar a condição.' } as Record<string, string>)[selected.work_order.reevaluation.resultado] : 'A reavaliação ainda não foi executada.'}</p></section>
            {error && <p role="alert" className="mt-3 text-sm text-[color:var(--status-critico)]">{error}</p>}
            <div className="mt-4 flex flex-wrap gap-2">{selected.transicoes_permitidas.map((status) => <button data-testid={`decision-action-${status}`} key={status} type="button" disabled={saving} onClick={() => void changeStatus(status)} className="btn-brand min-h-10 rounded-xl px-4 text-xs font-bold disabled:opacity-50">{saving ? 'Salvando...' : actionLabel[status] ?? statusLabel[status]}</button>)}</div>
            <section data-testid="decision-audit" className="mt-6 border-t border-[var(--line)] pt-4"><h3 className="section-heading">Linha do tempo</h3>{selected.historico?.length ? <ol className="mt-3 space-y-3">{selected.historico.map((item, index) => <li key={`${item.quando}-${index}`} className="border-l-2 border-[color:var(--ui-accent)]/40 pl-3 text-sm"><p className="font-semibold text-[var(--text-1)]">{{'decision.approve':'Aprovada','decision.reject':'Rejeitada','decision.execute':'Execução registrada','decision.expirada':'Expirada'}[item.action] ?? item.action}</p><p className="text-xs text-[var(--text-3)]">{item.ator ?? 'Sistema'} · {new Date(item.quando).toLocaleString('pt-BR')}</p></li>)}</ol> : <p className="mt-2 text-sm text-[var(--text-3)]">Nenhuma movimentação registrada.</p>}</section>
          </>}
        </section>
      </div>}
  </AppShell>;
}

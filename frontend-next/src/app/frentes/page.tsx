'use client';

import { useEffect, useState } from 'react';
import { Network, Plus, Upload } from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { operationGraphService, type OperationGraph } from '@/services/operationGraphService';

const initialForm = { origem: '', destino: '', tipo: 'ALIMENTA', front: '', de: '', ate: '' };

export default function FrentesPage() {
  const [graph, setGraph] = useState<OperationGraph | null>(null);
  const [form, setForm] = useState(initialForm);
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const reload = () => operationGraphService.get().then(setGraph).catch((cause: Error) => setError(cause.message)).finally(() => setLoading(false));
  useEffect(() => { reload(); }, []);

  async function submit(event: React.FormEvent) {
    event.preventDefault(); setError(''); setMessage('');
    try { await operationGraphService.create(form); setMessage('Relação gravada. O grafo ganhou mais uma aresta, sem precisar de SQL.'); setForm(initialForm); await reload(); } catch (cause) { setError((cause as Error).message); }
  }

  async function importFile() {
    if (!file) return;
    setError(''); setMessage('');
    try { const result = await operationGraphService.importCsv(file); setMessage(`${result.gravado} relação(ões) gravada(s); ${result.rejeitadas?.length ?? 0} rejeitada(s).`); await reload(); } catch (cause) { setError((cause as Error).message); }
  }

  return (
    <AppShell active="/frentes" eyebrow="Operação" title="Frentes e equipes" description="Associe máquinas ao contexto operacional do turno.">
      <div className="space-y-5">
        {message ? <p role="status" className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-700">{message}</p> : null}
        {error ? <p role="alert" className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-700">{error}</p> : null}
        <section className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <form onSubmit={submit} className="rounded-3xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-5 shadow-sm">
            <div className="mb-5 flex items-start gap-3"><Network size={20} className="mt-1 text-[color:var(--ui-accent)]" /><div><h2 className="text-lg font-bold text-[var(--text-1)]">Nova associação</h2><p className="text-sm text-[var(--text-3)]">Primeira versão: formulário direto, porque o grafo não precisa de uma nave espacial.</p></div></div>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="text-sm text-[var(--text-2)]">Origem<select required value={form.origem} onChange={e => setForm({ ...form, origem: e.target.value })} className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--background)] p-3"><option value="">Selecione</option>{graph?.machines.map(machine => <option key={machine.id} value={machine.external_code}>{machine.external_code} · {machine.tipo ?? 'tipo não informado'}</option>)}</select></label>
              <label className="text-sm text-[var(--text-2)]">Destino<select required value={form.destino} onChange={e => setForm({ ...form, destino: e.target.value })} className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--background)] p-3"><option value="">Selecione</option>{graph?.machines.map(machine => <option key={machine.id} value={machine.external_code}>{machine.external_code} · {machine.tipo ?? 'tipo não informado'}</option>)}</select></label>
              <label className="text-sm text-[var(--text-2)]">Tipo<select value={form.tipo} onChange={e => setForm({ ...form, tipo: e.target.value })} className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--background)] p-3"><option value="ALIMENTA">Alimenta</option><option value="TRANSPORTA_PARA">Transporta para</option><option value="DEPENDE_DE">Depende de</option></select></label>
              <label className="text-sm text-[var(--text-2)]">Frente<select value={form.front} onChange={e => setForm({ ...form, front: e.target.value })} className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--background)] p-3"><option value="">Sem frente</option>{graph?.fronts.map(front => <option key={front.id} value={front.id}>{front.nome}</option>)}</select></label>
              <label className="text-sm text-[var(--text-2)]">Válido de<input required type="datetime-local" value={form.de} onChange={e => setForm({ ...form, de: e.target.value })} className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--background)] p-3" /></label>
              <label className="text-sm text-[var(--text-2)]">Válido até <span className="text-xs text-[var(--text-3)]">(opcional)</span><input type="datetime-local" value={form.ate} onChange={e => setForm({ ...form, ate: e.target.value })} className="mt-1 w-full rounded-xl border border-[var(--line)] bg-[var(--background)] p-3" /></label>
            </div>
            <button className="mt-5 inline-flex min-h-11 items-center gap-2 rounded-xl bg-[var(--ui-accent)] px-4 text-sm font-bold text-black" type="submit"><Plus size={17} /> Gravar associação</button>
          </form>
          <section className="rounded-3xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-5 shadow-sm"><div className="mb-4 flex items-start gap-3"><Upload size={20} className="mt-1 text-[color:var(--ui-accent)]" /><div><h2 className="text-lg font-bold text-[var(--text-1)]">Importar CSV</h2><p className="text-sm text-[var(--text-3)]">Cabeçalho: origem,destino,tipo,front,de,ate</p></div></div><input type="file" accept=".csv,text/csv" onChange={e => setFile(e.target.files?.[0] ?? null)} className="block w-full text-sm text-[var(--text-2)]" /><button disabled={!file} onClick={importFile} className="mt-5 inline-flex min-h-11 items-center gap-2 rounded-xl border border-[var(--line)] px-4 text-sm font-bold text-[var(--text-1)] disabled:cursor-not-allowed disabled:opacity-40"><Upload size={17} /> Validar e importar</button></section>
        </section>
        <section className="rounded-3xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-5 shadow-sm"><div className="mb-4 flex items-center justify-between"><h2 className="text-lg font-bold text-[var(--text-1)]">Relações cadastradas</h2><span className="text-xs text-[var(--text-3)]">{loading ? 'carregando…' : `${graph?.links.length ?? 0} relação(ões)`}</span></div><div className="overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><thead className="text-xs uppercase tracking-wider text-[var(--text-3)]"><tr><th className="py-2">Origem</th><th>Tipo</th><th>Destino</th><th>Frente</th><th>Vigência</th></tr></thead><tbody>{graph?.links.map(link => <tr key={link.id} className="border-t border-[var(--line)] text-[var(--text-2)]"><td className="py-3 font-semibold">{link.origem}</td><td>{link.tipo}</td><td>{link.destino}</td><td>{graph.fronts.find(front => front.id === link.front)?.nome ?? 'Sem frente'}</td><td>{new Date(link.de).toLocaleString('pt-BR')} → {link.ate ? new Date(link.ate).toLocaleString('pt-BR') : 'aberta'}</td></tr>)}</tbody></table>{!loading && !graph?.links.length ? <p className="py-8 text-center text-sm text-[var(--text-3)]">Ainda não há relações. O grafo está quieto, não quebrado.</p> : null}</div></section>
      </div>
    </AppShell>
  );
}

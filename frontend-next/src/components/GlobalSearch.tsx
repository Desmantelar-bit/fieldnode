'use client';

import Link from 'next/link';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Search, X } from 'lucide-react';
import { searchGlobal } from '@/services/searchService';
import type { GlobalSearch } from '@/schemas/busca';

const groups = [
  ['machines', 'Máquinas'],
  ['operators', 'Operários'],
  ['decisions', 'Decisões'],
] as const;

export function GlobalSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [data, setData] = useState<GlobalSearch | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault(); setOpen(true);
      } else if (event.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  useEffect(() => { if (open) window.setTimeout(() => inputRef.current?.focus(), 0); }, [open]);
  useEffect(() => {
    if (!open || query.trim().length < 2) { setData(null); setError(''); setLoading(false); return; }
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setLoading(true); setError('');
      try { setData(await searchGlobal(query.trim(), controller.signal)); setActiveIndex(0); }
      catch (err) { if (!controller.signal.aborted) setError(err instanceof Error ? err.message : 'Busca indisponível.'); }
      finally { if (!controller.signal.aborted) setLoading(false); }
    }, 220);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [open, query]);

  const items = useMemo(() => data ? groups.flatMap(([key]) => data.results[key]) : [], [data]);
  function onInputKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'ArrowDown') { event.preventDefault(); setActiveIndex((value) => Math.min(value + 1, Math.max(items.length - 1, 0))); }
    if (event.key === 'ArrowUp') { event.preventDefault(); setActiveIndex((value) => Math.max(value - 1, 0)); }
    if (event.key === 'Enter' && items[activeIndex]) window.location.assign(items[activeIndex].href);
  }

  return <>
    <button type="button" onClick={() => setOpen(true)} aria-label="Buscar máquinas, operários e decisões" title="Busca global · Ctrl+K" className="global-search-trigger hidden min-h-9 items-center gap-2 rounded-xl border px-3 text-xs font-semibold sm:inline-flex">
      <Search size={14} aria-hidden="true" /> <span>Buscar</span><kbd className="hidden rounded border px-1.5 py-0.5 text-[10px] font-medium lg:inline">Ctrl K</kbd>
    </button>
    {open ? <div className="fixed inset-0 z-[100] bg-black/55 p-4 sm:p-8" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
      <section role="dialog" aria-modal="true" aria-labelledby="global-search-title" className="global-search-dialog mx-auto mt-[7vh] w-full max-w-2xl overflow-hidden rounded-2xl border shadow-2xl">
        <h2 id="global-search-title" className="sr-only">Busca global</h2>
        <div className="flex items-center gap-3 border-b px-4"><Search size={18} aria-hidden="true" className="text-[color:var(--ui-accent)]" /><input ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={onInputKeyDown} placeholder="Buscar máquina, operário ou decisão" aria-label="Buscar" className="min-h-14 min-w-0 flex-1 bg-transparent text-base outline-none" /><button type="button" onClick={() => setOpen(false)} aria-label="Fechar busca" className="rounded-lg p-2 text-[var(--text-3)] hover:text-[var(--text-1)]"><X size={18} aria-hidden="true" /></button></div>
        <div className="max-h-[60vh] overflow-y-auto p-3" aria-live="polite">
          {loading ? <p className="px-3 py-8 text-center text-sm text-[var(--text-3)]">Consultando registros…</p> : error ? <p role="alert" className="px-3 py-8 text-center text-sm text-[color:var(--status-critico)]">{error}</p> : query.trim().length < 2 ? <p className="px-3 py-8 text-center text-sm text-[var(--text-3)]">Digite pelo menos 2 caracteres.</p> : !items.length ? <p className="px-3 py-8 text-center text-sm text-[var(--text-3)]">Nenhum registro encontrado.</p> : groups.map(([key, label]) => data?.results[key].length ? <section key={key} aria-labelledby={`search-${key}`} className="mb-3 last:mb-0"><h3 id={`search-${key}`} className="px-3 py-2 text-[10px] font-bold uppercase tracking-[0.12em] text-[var(--text-3)]">{label}</h3>{data.results[key].map((item) => { const index = items.findIndex((candidate) => candidate.id === item.id); return <Link key={item.id} href={item.href} onClick={() => setOpen(false)} className={`block rounded-xl px-3 py-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[color:var(--ui-accent)] ${index === activeIndex ? 'bg-[var(--panel-glass-strong)]' : 'hover:bg-[var(--panel-glass-mid)]'}`}><p className="text-sm font-semibold text-[var(--text-1)]">{item.label}</p><p className="mt-0.5 text-xs text-[var(--text-3)]">{item.description}</p></Link>; })}</section> : null)}
        </div>
        <p className="border-t px-4 py-2 text-[10px] text-[var(--text-3)]">↑ ↓ navegar · Enter abrir · Esc fechar</p>
      </section>
    </div> : null}
  </>;
}

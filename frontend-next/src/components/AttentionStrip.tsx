'use client';

import Link from 'next/link';
import { useCallback } from 'react';
import { ArrowRight, ShieldAlert } from 'lucide-react';
import { attentionService } from '@/services/attentionService';
import { usePolling } from '@/lib/usePolling';
import { classifyAttention } from '@/lib/attentionPriority';
import { StatusBadge } from '@/components/StatusBadge';

const bandLabels = { P1: 'Prioridade 1', P2: 'Prioridade 2', P3: 'Prioridade 3' };

export function AttentionStrip() {
  const fetchSummary = useCallback((signal: AbortSignal) => attentionService.get(signal), []);
  const { data, error, loading } = usePolling(fetchSummary, 5000);

  return (
    <section aria-labelledby="attention-title" className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4 sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <ShieldAlert size={17} aria-hidden="true" className="text-[color:var(--status-atencao)]" />
            <p className="section-heading">Atenção agora</p>
          </div>
          <h2 id="attention-title" className="mt-1 text-lg font-semibold text-[var(--text-1)]">
            O que exige atenção na operação
          </h2>
          {loading && !data ? <p role="status" className="mt-2 text-sm text-[var(--text-3)]">Carregando resumo operacional…</p> : null}
          {error && !data ? <p role="alert" className="mt-2 text-sm text-[var(--text-2)]">Resumo indisponível; não há contagens atuais.</p> : null}
          {data ? (
            <ul className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm text-[var(--text-2)]" aria-label="Contagens atuais de atenção">
              <li><strong className="tabular-nums text-[var(--text-1)]">{data.decisoes_pendentes}</strong> decisões pendentes</li>
              <li><strong className="tabular-nums text-[var(--text-1)]">{data.riscos_criticos}</strong> riscos críticos</li>
              <li><strong className="tabular-nums text-[var(--text-1)]">{data.eventos_criticos}</strong> eventos críticos</li>
              <li><strong className="tabular-nums text-[var(--text-1)]">{data.maquinas_dados_instaveis}</strong> máquinas com confiança baixa</li>
            </ul>
          ) : null}
          {data?.eventos.length ? (
            <ol className="mt-4 space-y-2 border-t border-[var(--line)] pt-3" aria-label="Eventos abertos ordenados por prioridade">
              {data.eventos.map((event) => {
                const band = classifyAttention(event.priority_score, event.severidade);
                return (
                  <li key={event.id} className="flex flex-wrap items-center gap-2 text-sm">
                    <StatusBadge tone={band === 'P1' ? 'critical' : band === 'P2' ? 'warning' : 'muted'}>
                      {band ? `${band} · ${bandLabels[band]}` : 'Prioridade indisponível'}
                    </StatusBadge>
                    <span className="font-semibold text-[var(--text-1)]">{event.machine_external_code}</span>
                    <span className="text-[var(--text-2)]">{event.tipo.replaceAll('_', ' ').toLowerCase()}</span>
                    {event.needs_verification ? <StatusBadge tone="warning">Verificar sensor</StatusBadge> : null}
                  </li>
                );
              })}
            </ol>
          ) : null}
        </div>
        <Link href="/maquinas" className="inline-flex min-h-10 shrink-0 items-center gap-2 rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] px-3.5 py-2 text-xs font-semibold text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)]">
          Resolver agora <ArrowRight size={14} aria-hidden="true" />
        </Link>
      </div>
      {error && data ? <p role="status" className="mt-3 text-xs text-[color:var(--status-atencao)]">Atualização falhou; mostrando o último resumo disponível.</p> : null}
      <p className="mt-3 text-[10px] text-[var(--text-3)]">Bandas P1/P2/P3 são heurísticas não calibradas. Dados atualizados a cada 5 segundos.</p>
    </section>
  );
}

'use client';

import { useCallback, useEffect, useState } from 'react';
import { telemetryService } from '@/services/telemetryService';
import type { OperationalEvent } from '@/schemas/events';
import { StatusBadge, riskTone } from '@/components/StatusBadge';

export function PriorityEvents() {
  const [events, setEvents] = useState<OperationalEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stale, setStale] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await telemetryService.getPriorityEvents();
      setEvents(data);
      setUpdatedAt(new Date().toISOString());
      setError(null);
      setStale(false);
    } catch {
      setStale(true);
      setError('Não foi possível atualizar os eventos prioritários.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), 30000);
    return () => window.clearInterval(id);
  }, [refresh]);

  return (
    <section aria-labelledby="priority-events-title" className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-4 sm:p-5">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="section-heading">Atenção operacional</p>
          <h2 id="priority-events-title" className="mt-1 text-lg font-semibold text-[var(--text-1)]">Eventos prioritários</h2>
        </div>
        {updatedAt && (
          <p className="text-[10px] text-[var(--text-3)]" aria-live="polite">
            {stale ? 'Últimos dados disponíveis · ' : 'Atualizado · '}
            {new Date(updatedAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>

      {loading ? (
        <p role="status" className="py-3 text-sm text-[var(--text-3)]">Carregando eventos prioritários…</p>
      ) : error && events.length === 0 ? (
        <div role="alert" className="flex flex-wrap items-center justify-between gap-3 py-2">
          <p className="text-sm text-[var(--text-2)]">{error}</p>
          <button type="button" onClick={() => void refresh()} className="text-xs font-semibold underline">Tentar novamente</button>
        </div>
      ) : events.length === 0 ? (
        <p className="py-3 text-sm text-[var(--text-3)]">Nenhum evento prioritário registrado.</p>
      ) : (
        <ol className="divide-y divide-[var(--line)]" aria-label="Eventos ordenados por prioridade de atenção">
          {events.map((event) => (
            <li key={event.id} className="flex flex-wrap items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
              <div className="flex min-w-0 flex-wrap items-center gap-2">
                <StatusBadge tone={riskTone(event.severidade)}>{event.severidade}</StatusBadge>
                <span className="text-sm font-semibold text-[var(--text-1)]">{event.machine_external_code}</span>
                <span className="text-xs text-[var(--text-2)]">{event.tipo.replaceAll('_', ' ').toLowerCase()}</span>
                {event.needs_verification && (
                  <StatusBadge tone="warning">
                    {event.evidence_quality === 'suspeita' ? 'Evidência suspeita' : 'Verificar leitura'}
                  </StatusBadge>
                )}
              </div>
              <div className="flex shrink-0 items-baseline gap-2 text-xs text-[var(--text-3)]">
                <span>Prioridade</span>
                <strong className="text-sm tabular-nums text-[var(--text-1)]">
                  {event.priority_score === null ? '—' : event.priority_score.toFixed(2)}
                </strong>
              </div>
            </li>
          ))}
        </ol>
      )}
      {error && events.length > 0 ? <p role="status" className="mt-3 text-[10px] text-[var(--status-atencao)]">Atualização falhou; exibindo os últimos dados conhecidos.</p> : null}
    </section>
  );
}

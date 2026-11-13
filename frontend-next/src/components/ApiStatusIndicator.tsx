'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

type QueueItem = { localId: string; state: string; last_error?: string | null };
type QueueCounts = { pending: number; retrying: number; rejected: number; auth_blocked: number };
const EMPTY_QUEUE: QueueCounts = { pending: 0, retrying: 0, rejected: 0, auth_blocked: 0 };

export function ApiStatusIndicator() {
  const [isOnline, setIsOnline] = useState(true);
  const [queue, setQueue] = useState<QueueCounts | null>(null);
  const [rejectedItems, setRejectedItems] = useState<QueueItem[]>([]);
  const [authRequired, setAuthRequired] = useState(false);
  const [queueError, setQueueError] = useState(false);

  useEffect(() => {
    let active = true;

    async function check() {
      try {
        const headers = new Headers({ Accept: 'application/json' });
        const res = await fetch(`/api/health/`, {
          signal: AbortSignal.timeout(3000),
          cache: 'no-store',
          headers,
        });

        if (res.ok) {
          const data = await res.json().catch(() => ({}));
          if (active) setIsOnline(data.status === 'ok' || res.status === 200);
          return;
        }

        // Se o endpoint /health/ não existe (404), verifica a raiz de telemetria
        if (res.status === 404) {
          const fallbackRes = await fetch(`/api/colheitadeira/`, {
            method: 'HEAD',
            signal: AbortSignal.timeout(3000),
            cache: 'no-store',
            headers,
          }).catch(() => null);

          if (active) {
            // Qualquer resposta HTTP < 500 comprova que o backend está ativo e respondendo
            setIsOnline(fallbackRes !== null && fallbackRes.status < 500);
          }
          return;
        }

        if (active) setIsOnline(false);
      } catch {
        if (active) setIsOnline(false);
      }
    }

    check();
    const id = setInterval(check, 15000);
    return () => { active = false; clearInterval(id); };
  }, []);

  useEffect(() => {
    const controller = navigator.serviceWorker?.controller;
    const requestStatus = () => navigator.serviceWorker?.controller?.postMessage({ type: 'GET_TELEMETRY_STATUS' });
    const onQueue = (event: Event) => {
      const detail = (event as CustomEvent<{ counts?: QueueCounts; items?: QueueItem[] }>).detail;
      if (detail?.counts) setQueue({ ...EMPTY_QUEUE, ...detail.counts });
      if (detail?.items) setRejectedItems(detail.items.filter((item) => item.state === 'rejected'));
      setQueueError(false);
    };
    const onAuth = () => setAuthRequired(true);
    const onAuthRecovered = () => setAuthRequired(false);
    const onQueueError = () => setQueueError(true);
    window.addEventListener('fieldnode-queue-status', onQueue);
    window.addEventListener('fieldnode-auth-required', onAuth);
    window.addEventListener('fieldnode-auth-recovered', onAuthRecovered);
    window.addEventListener('fieldnode-queue-error', onQueueError);
    controller?.postMessage({ type: 'GET_TELEMETRY_STATUS' });
    const refreshId = window.setInterval(requestStatus, 15000);
    return () => {
      window.removeEventListener('fieldnode-queue-status', onQueue);
      window.removeEventListener('fieldnode-auth-required', onAuth);
      window.removeEventListener('fieldnode-auth-recovered', onAuthRecovered);
      window.removeEventListener('fieldnode-queue-error', onQueueError);
      window.clearInterval(refreshId);
    };
  }, []);

  function reprocessRejected() {
    navigator.serviceWorker?.controller?.postMessage({ type: 'REPROCESS_REJECTED' });
    window.setTimeout(() => navigator.serviceWorker?.controller?.postMessage({ type: 'GET_TELEMETRY_STATUS' }), 100);
  }

  return (
    <div className="status-pill flex items-center gap-1.5 border px-2.5 py-1.5">
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isOnline
            ? 'bg-[color:var(--status-normal)] shadow-[0_0_6px_var(--glow-normal-strong)]'
            : 'animate-pulse bg-[color:var(--status-critico)]'
        }`}
      />
      <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
        API {isOnline ? 'online' : 'offline'}
      </span>
      {queue && (queue.pending + queue.retrying + queue.rejected + queue.auth_blocked > 0) && (
        <div className="ml-2 border-l border-current/20 pl-2 text-[10px]" aria-live="polite">
          <span>{queue.pending} pendentes · {queue.retrying} retentativas</span>
          {queue.rejected > 0 && <span className="ml-1 text-[color:var(--status-critico)]">· {queue.rejected} rejeitadas</span>}
          {queue.auth_blocked > 0 && <span className="ml-1 text-[color:var(--status-atencao)]">· {queue.auth_blocked} aguardam login</span>}
        </div>
      )}
      {queue?.rejected ? (
        <details className="ml-2 text-[10px]">
          <summary className="cursor-pointer underline">Ver erros</summary>
          <ul className="absolute z-50 max-h-40 overflow-auto rounded bg-[var(--panel)] p-2 shadow-lg">
            {rejectedItems.map((item) => <li key={item.localId}>{item.localId.slice(0, 8)}: {item.last_error || 'Erro permanente'}</li>)}
          </ul>
        </details>
      ) : null}
      {queue?.rejected ? <button type="button" onClick={reprocessRejected} className="ml-2 text-[10px] underline">Reprocessar rejeitadas</button> : null}
      {(authRequired || (queue?.auth_blocked ?? 0) > 0) && (
        <span className="ml-2 text-[10px]" role="status">
          Autenticação necessária. <Link href="/login" className="underline">Entrar</Link>
        </span>
      )}
      {queueError ? <span className="ml-2 text-[10px]" role="alert">Não foi possível ler a fila offline.</span> : null}
      {queue === null && !queueError && <span className="sr-only" role="status">Estado da fila offline ainda não disponível</span>}
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';

export function ApiStatusIndicator() {
  const [isOnline, setIsOnline] = useState(true);
  const [queue, setQueue] = useState({
    pending: 0,
    retrying: 0,
    rejected: 0,
    auth_blocked: 0,
  });

  useEffect(() => {
    let active = true;

    function onWorkerMessage(event: MessageEvent) {
      const message = event.data;
      if (
        message?.type === "TELEMETRY_QUEUE_STATUS" ||
        message?.type === "TELEMETRY_SYNC_RESULT"
      ) {
        setQueue({
          pending: Number(message.pending) || 0,
          retrying: Number(message.retrying) || 0,
          rejected: Number(message.rejected) || 0,
          auth_blocked: Number(message.auth_blocked) || 0,
        });
      }
    }

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.addEventListener("message", onWorkerMessage);
      navigator.serviceWorker.ready.then((registration) => {
        const worker =
          navigator.serviceWorker.controller || registration.active;
        if (!worker || !active) return;
        const channel = new MessageChannel();
        channel.port1.onmessage = onWorkerMessage;
        worker.postMessage({ type: "GET_TELEMETRY_QUEUE_STATUS" }, [
          channel.port2,
        ]);
      });
    }

    async function check() {
      try {
        const headers = new Headers({ Accept: "application/json" });
        const res = await fetch(`/api/health/`, {
          signal: AbortSignal.timeout(3000),
          cache: "no-store",
          headers,
        });

        if (res.ok) {
          const data = await res.json().catch(() => ({}));
          if (active) setIsOnline(data.status === "ok" || res.status === 200);
          return;
        }

        // Se o endpoint /health/ não existe (404), verifica a raiz de telemetria
        if (res.status === 404) {
          const fallbackRes = await fetch(`/api/colheitadeira/`, {
            method: "HEAD",
            signal: AbortSignal.timeout(3000),
            cache: "no-store",
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
    return () => {
      active = false;
      clearInterval(id);
      if ("serviceWorker" in navigator) {
        navigator.serviceWorker.removeEventListener("message", onWorkerMessage);
      }
    };
  }, []);

  function reprocessRejected() {
    navigator.serviceWorker?.controller?.postMessage({
      type: "REPROCESS_REJECTED_TELEMETRY",
    });
  }

  return (
    <div className="status-pill flex items-center gap-1.5 border px-2.5 py-1.5">
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isOnline
            ? "bg-[color:var(--status-normal)] shadow-[0_0_6px_var(--glow-normal-strong)]"
            : "animate-pulse bg-[color:var(--status-critico)]"
        }`}
      />
      <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
        API {isOnline ? "online" : "offline"}
      </span>
      {queue.pending + queue.retrying + queue.rejected + queue.auth_blocked >
      0 ? (
        <span aria-live="polite" className="text-[10px] text-[var(--text-2)]">
          Fila: {queue.pending + queue.retrying} pendente(s), {queue.rejected}{" "}
          rejeitada(s), {queue.auth_blocked} aguardando login
        </span>
      ) : null}
      {queue.rejected > 0 ? (
        <button
          type="button"
          onClick={reprocessRejected}
          className="text-[10px] font-semibold text-[var(--text-1)] underline underline-offset-2"
        >
          Reprocessar rejeitadas
        </button>
      ) : null}
    </div>
  );
}

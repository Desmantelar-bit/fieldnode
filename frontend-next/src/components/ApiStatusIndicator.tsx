'use client';

import { useEffect, useState } from 'react';

export function ApiStatusIndicator() {
  const [isOnline, setIsOnline] = useState(true);

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
    </div>
  );
}

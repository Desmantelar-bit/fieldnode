'use client';

import { useEffect, useState } from 'react';
import { resolveApiUrl } from '@/services/telemetryService';

const API_URL = resolveApiUrl();

export function ApiStatusIndicator() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    let isActive = true;

    async function verificarAPI() {
      try {
        const res = await fetch(`${API_URL}/health/`, {
          signal: AbortSignal.timeout(3000),
          cache: 'no-store',
        });

        if (!res.ok) throw new Error('API Degradada');

        const data = await res.json();
        if (isActive) setIsOnline(data.status === 'ok');
      } catch {
        if (isActive) setIsOnline(false);
      }
    }

    verificarAPI();

    const intervalId = setInterval(verificarAPI, 15000);

    return () => {
      isActive = false;
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="flex w-fit items-center gap-2 rounded-full border border-white/10 bg-slate-900/50 px-3 py-1.5 backdrop-blur-md">
      <span
        className={`h-2 w-2 rounded-full ${
          isOnline
            ? 'bg-status-normal shadow-[0_0_8px_rgba(204,255,0,0.5)]'
            : 'animate-pulse bg-status-critico shadow-[0_0_8px_rgba(255,94,0,0.5)]'
        }`}
      />
      <span className="text-xs uppercase tracking-label text-slate-400">
        API {isOnline ? 'Online' : 'Offline'}
      </span>
    </div>
  );
}

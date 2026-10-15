'use client';

import { useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[FieldNode] Falha no dashboard:', error);
  }, [error]);

  return (
    <main className="min-h-screen bg-[var(--surface-page)] px-4 py-6 sm:px-6 lg:px-8">
      <section className="mx-auto flex min-h-[60vh] max-w-2xl flex-col items-center justify-center text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[color:var(--status-critico)]/10 text-[color:var(--status-critico)] shadow-[0_0_28px_var(--glow-red)]">
          <AlertTriangle size={24} strokeWidth={1.8} aria-hidden="true" />
        </div>
        <p className="mt-5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--status-critico)]">
          conexão indisponível
        </p>
        <h1 className="mt-2 text-xl font-bold text-[var(--text-1)]">
          o dashboard perdeu o sinal com a frota.
        </h1>
        <p className="mt-3 max-w-md text-sm leading-relaxed text-[var(--text-3)]">
          não conseguimos consultar os dados mais recentes da telemetria.
          verifique se o serviço da API está ativo e tente novamente.
        </p>
        <button
          type="button"
          onClick={reset}
          className="mt-6 rounded-xl bg-[var(--panel-glass-mid)] px-5 py-2.5 text-sm font-semibold text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] active:scale-95"
        >
          tentar novamente
        </button>
      </section>
    </main>
  );
}

'use client';

import { useEffect } from 'react';

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
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-8">
      <section className="mx-auto flex min-h-[60vh] max-w-3xl flex-col justify-center">
        <div className="rounded-lg border border-red-200 bg-white p-5 shadow-sm sm:p-6">
          <p className="text-sm font-semibold uppercase tracking-wide text-red-600">Falha ao carregar</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-950">O dashboard perdeu o fio da meada.</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Nao consegui buscar os dados da frota agora. Verifique se a API Django esta ligada e tente de novo.
          </p>
          <button
            type="button"
            onClick={reset}
            className="mt-5 inline-flex min-h-11 items-center rounded-md bg-slate-950 px-4 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            Tentar novamente
          </button>
        </div>
      </section>
    </main>
  );
}

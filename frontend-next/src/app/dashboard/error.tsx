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
    <main className="min-h-screen bg-slate-950 px-4 py-6 sm:px-6 lg:px-8">
      <section className="mx-auto flex min-h-[60vh] max-w-3xl flex-col justify-center">
        <div className="rounded-lg border border-red-300/20 bg-red-300/10 p-6">
          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-red-200">
            ✗ API indisponivel
          </p>
          <h1 className="mt-2 text-lg font-semibold text-slate-100">O dashboard perdeu o fio da meada.</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-red-100/75">
            Nao consegui buscar os dados da frota agora. Verifique se a API Django esta ligada e tente de novo.
          </p>
          <button
            type="button"
            onClick={reset}
            className="mt-5 border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]"
          >
            Tentar novamente
          </button>
        </div>
      </section>
    </main>
  );
}

'use client';

import { useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';

/**
 * Boundary de erro global do FieldNode (Next.js App Router).
 * Captura exceções não tratadas em qualquer rota.
 * Renderizado no lado do cliente obrigatoriamente (Next.js requirement).
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Registro para diagnóstico — nunca exibe stack trace ao usuário.
    console.error('[FieldNode] Erro global:', error?.digest ?? error?.message);
  }, [error]);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-12 bg-[var(--background)]">
      <div className="w-full max-w-md text-center">
        {/* Ícone */}
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-[color:var(--status-critico)]/10 text-[color:var(--status-critico)] shadow-[0_0_28px_rgba(255,92,92,0.15)]">
          <AlertTriangle size={28} strokeWidth={1.5} aria-hidden="true" />
        </div>

        {/* Rótulo */}
        <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[color:var(--status-critico)] mb-2">
          sinal interrompido
        </p>

        {/* Título */}
        <h1 className="text-2xl font-bold text-[var(--text-1)] mb-3">
          não conseguimos alcançar essa parte do sistema agora.
        </h1>

        {/* Descrição — sem expor detalhes internos */}
        <p className="text-sm leading-relaxed text-[var(--text-3)] mb-8">
          ocorreu uma instabilidade inesperada na interface ou na comunicação.
          você pode tentar restabelecer a conexão ou retornar à visão geral.
        </p>

        {/* Ações */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            type="button"
            onClick={reset}
            className="inline-flex items-center justify-center rounded-xl bg-[var(--lime)] px-6 py-2.5 text-sm font-semibold text-[var(--brand-on-accent)] transition hover:brightness-110 active:scale-95"
          >
            tentar restabelecer
          </button>
          <a
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-xl bg-[var(--panel-glass-mid)] px-6 py-2.5 text-sm font-semibold text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] active:scale-95"
          >
            ir para o dashboard
          </a>
        </div>

        {/* Digest para suporte (sem stack trace) */}
        {error?.digest && (
          <p className="mt-8 text-xs text-[var(--muted)]">
            referência de rastreio: {error.digest}
          </p>
        )}

        {/* Marca */}
        <p className="mt-4 text-xs text-[var(--muted)]">
          fieldnode · inteligência operacional
        </p>
      </div>
    </main>
  );
}

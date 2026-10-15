import Link from 'next/link';
import { Compass } from 'lucide-react';

/**
 * Página 404 global do FieldNode (Next.js App Router).
 * Renderizada automaticamente para qualquer rota não encontrada.
 */
export default function NotFound() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-12 bg-[var(--background)]">
      <div className="w-full max-w-md text-center">
        {/* Ícone */}
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-[color:var(--lime)]/10 text-[color:var(--lime)] shadow-[0_0_28px_rgba(167,255,44,0.15)]">
          <Compass size={28} strokeWidth={1.5} aria-hidden="true" />
        </div>

        {/* Código */}
        <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[color:var(--lime)] mb-2">
          coordenada não mapeada · 404
        </p>

        {/* Título */}
        <h1 className="text-2xl font-bold text-[var(--text-1)] mb-3">
          parece que este caminho não leva a lugar nenhum.
        </h1>

        {/* Descrição */}
        <p className="text-sm leading-relaxed text-[var(--text-3)] mb-8">
          o endereço acessado não corresponde a nenhuma máquina, rota ou recurso ativo.
          verifique a URL digitada ou retorne à operação central.
        </p>

        {/* Ações */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-xl bg-[var(--lime)] px-6 py-2.5 text-sm font-semibold text-[var(--brand-on-accent)] transition hover:brightness-110 active:scale-95"
          >
            ir para o dashboard
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-xl bg-[var(--panel-glass-mid)] px-6 py-2.5 text-sm font-semibold text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] active:scale-95"
          >
            acessar login
          </Link>
        </div>

        {/* Marca */}
        <p className="mt-12 text-xs text-[var(--muted)]">
          fieldnode · inteligência operacional
        </p>
      </div>
    </main>
  );
}

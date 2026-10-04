'use client';

import { useEffect } from 'react';
import { ErrorState } from "@/components/ui/FeedbackStates";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[FieldNode] Falha no dashboard:", error);
  }, [error]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-6 sm:px-6 lg:px-8">
      <section className="w-full max-w-3xl">
        <ErrorState
          title="O dashboard está indisponível."
          message="Não foi possível carregar os dados da frota. Verifique a conexão e tente novamente."
          onRetry={reset}
        />
      </section>
    </main>
  );
}

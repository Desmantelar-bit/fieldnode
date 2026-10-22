'use client';

import { ChevronLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function BackButton() {
  const router = useRouter();

  const handleBack = () => {
    if (window.history.length > 1) {
      router.back();
      return;
    }

    router.push('/dashboard');
  };

  return (
    <button
      type="button"
      onClick={handleBack}
      aria-label="Voltar para a página anterior"
      title="Voltar para a página anterior"
      className="-ml-1.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-[var(--text-3)] transition-colors hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] active:scale-95"
    >
      <ChevronLeft aria-hidden="true" size={20} strokeWidth={2} />
    </button>
  );
}

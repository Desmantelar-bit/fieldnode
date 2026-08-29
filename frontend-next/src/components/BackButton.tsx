'use client';

import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function BackButton() {
  const router = useRouter();

  return (
    <button
      type="button"
      onClick={() => router.back()}
      aria-label="Voltar para a tela anterior"
      title="Voltar"
      className="fixed left-4 top-4 z-40 inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-black/20 text-field-text2 shadow-lg backdrop-blur-xl transition hover:border-white/20 hover:bg-white/10 hover:text-field-text1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent active:scale-[0.97] lg:left-28"
    >
      <ArrowLeft aria-hidden="true" size={18} strokeWidth={1.8} />
    </button>
  );
}

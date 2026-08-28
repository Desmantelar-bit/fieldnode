'use client';

import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { glassPill } from '@/lib/design-tokens';

export function BackButton() {
  const router = useRouter();
  return <button type="button" onClick={() => router.back()} aria-label="Voltar" className={`fixed left-24 top-5 z-40 p-2.5 text-slate-300 transition hover:text-white lg:left-28 ${glassPill}`}><ArrowLeft size={17} /></button>;
}

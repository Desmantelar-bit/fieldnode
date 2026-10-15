"use client";

import dynamic from 'next/dynamic';
import { MapPin } from 'lucide-react';

const MapClient = dynamic(
  () => import('@/components/MapClient').then((mod) => mod.default),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-72 w-full items-center justify-center gap-3 text-[var(--text-3)]">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-[color:var(--ui-accent)] border-t-transparent" />
        <span className="text-xs font-semibold uppercase tracking-[0.1em]">Carregando mapa...</span>
      </div>
    ),
  }
);

export function FleetMap() {
  return (
    <section className="liquid-glass overflow-hidden">
      <div className="flex items-center gap-2.5 border-b border-[var(--line)] px-4 py-3">
        <MapPin size={14} className="text-[color:var(--ui-accent)]" aria-hidden="true" />
        <div>
          <h2 className="text-sm font-semibold text-[var(--text-1)]">Posição em campo</h2>
          <p className="text-[10px] text-[var(--text-3)]">
            Última localização conhecida por máquina
          </p>
        </div>
      </div>
      <div className="relative h-[50vh] min-h-[28rem] sm:h-[60vh]">
        <MapClient />
      </div>
    </section>
  );
}

"use client";

import dynamic from 'next/dynamic';

const FleetMap = dynamic(
  () => import('@/components/FleetMap').then((mod) => mod.FleetMap),
  {
    ssr: false,
    loading: () => (
      <div className="glass-panel flex h-[calc(100vh-5.5rem)] min-h-[28rem] w-full items-center justify-center border border-white/10 bg-white/[0.02] text-sm text-slate-400 sm:h-[calc(100vh-5rem)]">
        Carregando mapa...
      </div>
    ),
  }
);

export function MapaFrotaDynamic() {
  return <FleetMap />;
}

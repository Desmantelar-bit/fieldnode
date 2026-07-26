'use client';

import dynamic from 'next/dynamic';

const MapClient = dynamic(() => import('@/components/MapClient').then(mod => mod.default), { ssr: false });

export function FleetMap() {
  return (
    <section className="glass-panel border border-white/10 bg-white/[0.02] overflow-hidden">
      <div className="border-b border-white/10 px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-200">Posicao em campo</h2>
        <p className="mt-0.5 text-[11px] text-slate-500">
          Ultima localizacao conhecida por maquina (update a cada leitura).
        </p>
      </div>
      <MapClient />
    </section>
  );
}

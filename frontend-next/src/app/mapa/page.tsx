"use client";

import dynamic from "next/dynamic";
import { Sidebar } from "@/components/Sidebar";
import { glassCard, kpiLabel } from "@/lib/design-tokens";

const MapaFrota = dynamic(() => import("@/components/MapaFrota"), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center bg-base-950 text-sm text-slate-400">
      Carregando cartografia de campo...
    </div>
  ),
});

const fleetStatus = [
  { label: "Normal", value: 9, color: "bg-status-normal shadow-[0_0_8px_rgba(92,184,112,0.55)]" },
  { label: "Atenção", value: 2, color: "bg-status-atencao shadow-[0_0_8px_rgba(212,154,58,0.55)]" },
  { label: "Crítico", value: 1, color: "bg-status-critico shadow-[0_0_8px_rgba(181,77,77,0.55)]" },
] as const;

export default function MapaPage() {
  return (
    <main className="min-h-screen bg-base-950 text-white lg:ml-28">
      <Sidebar />
      <h1 className="sr-only">Mapa de frota</h1>

      <div className="relative h-[100dvh] min-h-screen overflow-hidden">
        <div className="absolute inset-0 z-0">
          <MapaFrota />
        </div>

        <aside
          aria-label="Status geral da frota"
          className={`absolute left-4 right-4 top-4 z-10 p-5 shadow-2xl sm:left-auto sm:right-6 sm:top-6 sm:w-80 ${glassCard}`}
        >
          <p className={kpiLabel}>Frota, status geral</p>
          <div className="mt-4 space-y-3">
            {fleetStatus.map(({ label, value, color }) => (
              <div key={label} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span aria-hidden="true" className={`h-2.5 w-2.5 rounded-full ${color}`} />
                  <span className="text-xs text-slate-300">{label}</span>
                </div>
                <span className="text-sm font-bold text-white">{value}</span>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </main>
  );
}

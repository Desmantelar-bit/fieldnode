"use client";

import dynamic from "next/dynamic";
import { AppShell } from "@/components/AppShell";
import { FileText } from "lucide-react";
import Link from "next/link";

const MapaFrota = dynamic(() => import("@/components/MapaFrota"), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-[var(--background)] text-[var(--text-3)]">
      <span className="h-8 w-8 animate-spin rounded-full border-2 border-[color:var(--ui-accent)] border-t-transparent" />
      <span className="text-xs font-semibold uppercase tracking-[0.1em]">
        Carregando cartografia...
      </span>
    </div>
  ),
});

export default function MapaPage() {
  return (
    <AppShell
      active="/mapa"
      eyebrow="FieldNode / Operação"
      title="Mapa de frota"
      description="Posição e status operacional das máquinas"
      actions={
        <Link href="/relatorios" className="btn-brand inline-flex min-h-10 items-center gap-2 rounded-xl px-3.5 text-xs font-bold">
          <FileText size={14} aria-hidden="true" />
          <span className="hidden sm:inline">Relatórios</span>
        </Link>
      }
      contentClassName="max-w-none px-0 py-0 sm:px-0 lg:px-0"
    >
      <h1 className="sr-only">Mapa de frota</h1>
      <div className="relative h-[calc(100dvh-5.25rem)] min-h-0 overflow-hidden">
        <MapaFrota />
      </div>
    </AppShell>
  );
}

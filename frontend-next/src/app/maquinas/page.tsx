"use client";

import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { FleetGrid } from "@/components/FleetGrid";
import { SkeletonGrid } from "@/components/SkeletonGrid";
import { telemetryService } from "@/services/telemetryService";
import type { Machine } from "@/types/telemetry";

export default function MaquinasPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [machines, setMachines] = useState<Machine[]>([]);

  const carregar = async () => {
    setLoading(true);
    setError(null);
    try {
      const dados = await telemetryService.getFleetStatus();
      setMachines(dados);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao carregar colheitadeiras.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
        <SkeletonGrid />
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
        <ErrorState title="Não consegui carregar a frota." message={error} />
      </AppShell>
    );
  }

  if (machines.length === 0) {
    return (
      <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
        <EmptyState
          title="Nenhuma máquina cadastrada."
          message="O sistema ainda não tem máquinas registradas. Cadastre na API ou execute o seed inicial."
        />
      </AppShell>
    );
  }

  return (
    <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          {machines.length} máquina{machines.length !== 1 ? "s" : ""} cadastrada{machines.length !== 1 ? "s" : ""}
        </p>
        <button
          onClick={carregar}
          className="rounded-md border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-semibold text-slate-200 transition hover:bg-white/[0.08]"
        >
          Atualizar
        </button>
      </div>
      <FleetGrid machines={machines} />
    </AppShell>
  );
}

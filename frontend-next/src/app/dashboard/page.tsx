"use client";

import { useEffect, useState } from "react";
import { telemetryService } from "@/services/telemetryService";
import { AppShell } from "@/components/AppShell";
import { ChatFAB } from "@/components/ChatFAB";
import { ErrorState } from "@/components/EmptyState";
import { FleetGrid } from "@/components/FleetGrid";
import { FleetMap } from "@/components/FleetMap";
import { ReportButton } from "@/components/ReportButton";
import { DashboardMachineData } from "@/components/DashboardMachineData";
import { FieldNodeLogo } from "@/components/FieldNodeLogo";
import { SkeletonGrid } from "@/components/SkeletonGrid";

type FleetStatus = Awaited<ReturnType<typeof telemetryService.getFleetStatus>>;
type TelemetryReadings = Awaited<ReturnType<typeof telemetryService.getLatestReadings>>;

export default function DashboardPage() {
  const [machines, setMachines] = useState<FleetStatus>([]);
  const [readings, setReadings] = useState<TelemetryReadings>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const m = await telemetryService.getFleetStatus();
        setMachines(m);
        try {
          const r = await telemetryService.getLatestReadings();
          setReadings(r);
        } catch {
          setReadings([]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Falha ao carregar dados do dashboard.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <AppShell
        active="/dashboard"
        title="Central de Operações"
        titleSlot={<FieldNodeLogo variant="horizontal" asLink={false} />}
      >
        <SkeletonGrid />
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell
        active="/dashboard"
        title="Central de Operações"
        titleSlot={<FieldNodeLogo variant="horizontal" asLink={false} />}
      >
        <ErrorState title="Dashboard indisponível" message={error} />
        <ChatFAB machines={machines} />
      </AppShell>
    );
  }

  return (
    <AppShell
      active="/dashboard"
      title="Central de Operações"
      titleSlot={<FieldNodeLogo variant="horizontal" asLink={false} />}
      actions={
        <div className="flex items-center gap-2">
          <ReportButton machines={machines} />
          <div className="status-pill status-pill--normal hidden items-center px-2.5 py-1.5 sm:flex">
            <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[color:var(--status-normal)]">
              Sync ativo
            </span>
          </div>
        </div>
      }
    >
      <div className="space-y-6">
        <DashboardMachineData machines={machines} initialReadings={readings} />

        <section aria-label="Resumo da frota">
          <p className="section-heading mb-3">Resumo da frota</p>
          <div className="fleet-summary grid grid-cols-3 gap-3 rounded-2xl p-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-[var(--text-1)]">{machines.length}</p>
              <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">Total</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[color:var(--status-normal)]">
                {machines.filter((m) => m.status_de_operacao.em_operacao).length}
              </p>
              <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">Ativos</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-[color:var(--status-atencao)]">
                {machines.filter((m) => !m.status_de_operacao.em_operacao).length}
              </p>
              <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">Inativos</p>
            </div>
          </div>
        </section>

        <section aria-label="Máquinas da frota">
          <p className="section-heading mb-3">Máquinas</p>
          <FleetGrid machines={machines} />
        </section>

        <section aria-label="Posição em campo">
          <p className="section-heading mb-3">Posição em campo</p>
          <FleetMap />
        </section>
      </div>
      <ChatFAB machines={machines} />
    </AppShell>
  );
}

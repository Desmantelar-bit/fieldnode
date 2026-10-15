'use client';

import { useEffect, useState } from 'react';
import { telemetryService } from '@/services/telemetryService';
import { AppShell } from '@/components/AppShell';
import { ChatFAB } from '@/components/ChatFAB';
import { ErrorState } from '@/components/EmptyState';
import { FleetGrid } from '@/components/FleetGrid';
import { FleetMap } from '@/components/FleetMap';
import { ReportButton } from '@/components/ReportButton';
import { DashboardMachineData } from '@/components/DashboardMachineData';
import { FieldNodeLogo } from '@/components/FieldNodeLogo';
import { SkeletonGrid } from '@/components/SkeletonGrid';

type FleetStatus = Awaited<ReturnType<typeof telemetryService.getFleetStatus>>;
type TelemetryReadings = Awaited<ReturnType<typeof telemetryService.getLatestReadings>>;

function FleetData({ machines, readings }: { machines: FleetStatus; readings: TelemetryReadings }) {
  return (
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
            <p className="text-2xl font-bold text-[color:var(--status-normal)]">{machines.filter((machine) => machine.status_de_operacao.em_operacao).length}</p>
            <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">Ativos</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-[color:var(--status-atencao)]">{machines.filter((machine) => !machine.status_de_operacao.em_operacao).length}</p>
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
  );
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<{
    loading: boolean;
    machines: FleetStatus;
    readings: TelemetryReadings;
    error: string | null;
  }>({ loading: true, machines: [], readings: [], error: null });

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      try {
        const machines = await telemetryService.getFleetStatus();
        const readings = await telemetryService.getLatestReadings().catch(() => []);
        if (active) setDashboard({ loading: false, machines, readings, error: null });
      } catch (err) {
        if (active) {
          setDashboard({
            loading: false,
            machines: [],
            readings: [],
            error: err instanceof Error ? err.message : 'Falha ao carregar dados do dashboard.',
          });
        }
      }
    }

    void loadDashboard();
    return () => { active = false; };
  }, []);

  if (dashboard.loading) {
    return (
      <AppShell active="/dashboard" title="Central de Operações">
        <SkeletonGrid />
      </AppShell>
    );
  }

  if (dashboard.error) {
    return (
      <AppShell
        active="/dashboard"
        title="Central de Operações"
        titleSlot={<FieldNodeLogo variant="horizontal" asLink={false} />}
      >
        <ErrorState title="Dashboard indisponível" message={dashboard.error} />
        <ChatFAB machines={dashboard.machines} />
      </AppShell>
    );
  }

  const { machines, readings } = dashboard;

  return (
    <AppShell
      active="/dashboard"
      title="Central de Operações"
      titleSlot={<FieldNodeLogo variant="horizontal" asLink={false} />}
      actions={
        <ReportButton machines={machines} />
      }
    >
      <FleetData machines={machines} readings={readings} />
      <ChatFAB machines={machines} />
    </AppShell>
  );
}

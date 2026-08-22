import { Suspense } from 'react';
import { telemetryService } from '@/services/telemetryService';
import { AppShell } from '@/components/AppShell';
import { ErrorState } from '@/components/EmptyState';
import { FleetGrid } from '@/components/FleetGrid';
import { FleetMap } from '@/components/FleetMap';
import { MetricCard } from '@/components/MetricCard';
import { ReportButton } from '@/components/ReportButton';
import { SkeletonGrid } from '@/components/SkeletonGrid';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

type FleetStatus = Awaited<ReturnType<typeof telemetryService.getFleetStatus>>;

async function FleetData() {
  let machines;

  try {
    machines = await telemetryService.getFleetStatus();
  } catch {
    return <ErrorState title="Nao consegui falar com a API agora." message="Confira se o backend Django esta rodando em 127.0.0.1:8000. O dashboard continua de pe, so esta sem dados frescos para mostrar." />;
  }

  const activeMachines = machines.filter((machine) => machine.status_de_operacao.em_operacao).length;
  const movingMachines = machines.filter((machine) => machine.estado_de_movimento.em_movimento).length;
  const totalHours = machines.reduce((sum, machine) => sum + machine.status_de_operacao.tempo_de_operacao, 0);

  return (
    <div className="space-y-6">
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricCard label="Maquinas" value={machines.length} helper="cadastradas na frota" />
        <MetricCard label="Em operacao" value={activeMachines} helper={`${movingMachines} em movimento`} tone="emerald" />
        <MetricCard label="Horas" value={`${totalHours.toFixed(1)}h`} helper="tempo total reportado" tone="amber" />
      </section>
      <FleetGrid machines={machines} />
      <FleetMap />
    </div>
  );
}

export default async function DashboardPage() {
  let reportMachines: FleetStatus = [];
  let reportError: string | null = null;

  try {
    reportMachines = await telemetryService.getFleetStatus();
  } catch (err) {
    reportError = err instanceof Error ? err.message : "Falha ao carregar dados do dashboard.";
  }

  if (reportError) {
    return (
      <AppShell active="/dashboard" eyebrow="FieldNode" title="Frota em campo">
        <ErrorState title="Dashboard indisponivel" message={reportError} />
      </AppShell>
    );
  }

  return (
    <AppShell
      active="/dashboard"
      eyebrow="FieldNode"
      title="Frota em campo"
      actions={
        <div className="inline-flex items-center gap-2">
          <ReportButton machines={reportMachines} />
          <div className="inline-flex items-center gap-2 border border-status-normal/20 bg-status-normal/15 px-3 py-1.5 text-xs font-semibold text-status-normal shadow-[0_0_18px_var(--glow-normal)] animate-pulse">
            <span className="h-2.5 w-2.5 bg-status-normal shadow-[0_0_6px_var(--glow-normal-strong)]" />
            Sync offline ativo
          </div>
        </div>
      }
    >
      <Suspense fallback={<SkeletonGrid />}>
        <FleetData />
      </Suspense>
    </AppShell>
  );
}

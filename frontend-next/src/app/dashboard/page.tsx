import { Suspense } from 'react';
import { telemetryService } from '@/services/telemetryService';
import { AppShell } from '@/components/AppShell';
import { ErrorState } from '@/components/EmptyState';
import { FleetGrid } from '@/components/FleetGrid';
import { FleetMap } from '@/components/FleetMap';
import { ReportButton } from '@/components/ReportButton';
import { SkeletonGrid } from '@/components/SkeletonGrid';
import { SparklineCard } from '@/components/SparklineCard';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

type FleetStatus = Awaited<ReturnType<typeof telemetryService.getFleetStatus>>;

const dadosRpm = [
  { valor: 1750 },
  { valor: 1800 },
  { valor: 1820 },
  { valor: 1790 },
  { valor: 1850 },
  { valor: 1820 },
];

const dadosTemperatura = [
  { valor: 72 },
  { valor: 74 },
  { valor: 76 },
  { valor: 79 },
  { valor: 82 },
  { valor: 78 },
];

const dadosVibracao = [
  { valor: 1.8 },
  { valor: 2.0 },
  { valor: 1.9 },
  { valor: 2.2 },
  { valor: 2.1 },
  { valor: 2.1 },
];

async function FleetData() {
  let machines;

  try {
    machines = await telemetryService.getFleetStatus();
  } catch {
    return <ErrorState title="Nao consegui falar com a API agora." message="Confira se o backend Django esta rodando em 127.0.0.1:8000. O dashboard continua de pe, so esta sem dados frescos para mostrar." />;
  }

  return (
    <div className="space-y-6">
      <section aria-label="Indicadores operacionais" className="grid grid-cols-12 gap-6">
        <div className="col-span-12 md:col-span-4">
          <SparklineCard titulo="RPM Médio" valor={1820} dados={dadosRpm} status="normal" />
        </div>
        <div className="col-span-12 md:col-span-4">
          <SparklineCard
            titulo="Temperatura do Motor"
            valor={78}
            unidade="°C"
            dados={dadosTemperatura}
            status="atencao"
          />
        </div>
        <div className="col-span-12 md:col-span-4">
          <SparklineCard titulo="Vibração do Rotor" valor={2.1} dados={dadosVibracao} status="normal" />
        </div>
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
      <AppShell active="/dashboard" eyebrow="FieldNode" title="Central de Operações">
        <ErrorState title="Dashboard indisponivel" message={reportError} />
      </AppShell>
    );
  }

  return (
    <AppShell
      active="/dashboard"
      eyebrow="FieldNode"
      title="Central de Operações"
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
      <p className="mb-8 text-sm text-field-text3">Monitoramento multivariado da frota em tempo real.</p>
      <Suspense fallback={<SkeletonGrid />}>
        <FleetData />
      </Suspense>
    </AppShell>
  );
}

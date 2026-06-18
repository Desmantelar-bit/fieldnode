import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { MetricCard } from '@/components/MetricCard';
import { TelemetryMachineCard } from '@/components/TelemetryMachineCard';
import { telemetryService } from '@/services/telemetryService';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function HarvestersPage() {
  let readings;

  try {
    readings = await telemetryService.getLatestReadings();
  } catch {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Operacao" title="Maquinas agricolas">
        <ErrorState title="Nao consegui carregar as maquinas." message="A API de ultimas leituras nao respondeu. Sem drama teatral: confira o Django e tente de novo." />
      </AppShell>
    );
  }

  const critical = readings.filter((reading) => reading.status_risco?.rotuloRisco === 'CRITICO').length;
  const warning = readings.filter((reading) => reading.status_risco?.rotuloRisco === 'ATENCAO').length;
  const averageTemp = readings.length ? readings.reduce((sum, reading) => sum + reading.temperatura, 0) / readings.length : 0;

  return (
    <AppShell active="/colheitadeiras" eyebrow="Operacao" title="Maquinas agricolas">
      <div className="space-y-5">
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <MetricCard label="Monitoradas" value={readings.length} helper="com leitura recente" />
          <MetricCard label="Alertas" value={critical + warning} helper={`${critical} criticos, ${warning} em atencao`} tone={critical ? 'red' : warning ? 'amber' : 'emerald'} />
          <MetricCard label="Temp media" value={`${averageTemp.toFixed(1)}C`} helper="entre leituras recentes" tone="amber" />
        </section>

        {readings.length === 0 ? (
          <EmptyState title="Nenhuma maquina encontrada." message="Quando a telemetria chegar, os cards aparecem aqui com temperatura, vibracao, RPM e risco." />
        ) : (
          <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {readings.map((reading) => (
              <TelemetryMachineCard key={reading.maquina_id} reading={reading} />
            ))}
          </section>
        )}
      </div>
    </AppShell>
  );
}

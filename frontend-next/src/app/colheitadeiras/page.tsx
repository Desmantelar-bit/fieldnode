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
        <ErrorState title="não conseguimos alcançar as máquinas." message="o serviço de telemetria não respondeu no momento. verifique se a API Django está ativa e tente novamente." />
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
          <EmptyState title="ainda não há sinais por aqui." message="assim que os pacotes de telemetria forem ingeridos, os cards aparecerão aqui com temperatura, vibração, RPM e status operacional." />
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

'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { MetricCard } from '@/components/MetricCard';
import { TelemetryMachineCard } from '@/components/TelemetryMachineCard';
import { LoadingState } from '@/components/ui/FeedbackStates';
import { telemetryService } from '@/services/telemetryService';
import type { Telemetry } from '@/types/telemetry';

export default function HarvestersPage() {
  const [readings, setReadings] = useState<Telemetry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    telemetryService.getLatestReadings().then((result) => {
      if (active) setReadings(result);
    }).catch(() => {
      if (active) setError('A API de últimas leituras não respondeu. Confira o Django e tente novamente.');
    });
    return () => { active = false; };
  }, []);

  if (error) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Operacao" title="Maquinas agricolas">
        <ErrorState title="Nao consegui carregar as maquinas." message={error} />
      </AppShell>
    );
  }

  if (!readings) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Operacao" title="Maquinas agricolas">
        <LoadingState mensagem="Carregando telemetria..." />
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

"use client";

import { useEffect, useState } from "react";
import { telemetryService } from "@/services/telemetryService";
import { AppShell } from "@/components/AppShell";
import { ChatFAB } from "@/components/ChatFAB";
import { ErrorState } from "@/components/EmptyState";
import { FleetGrid } from "@/components/FleetGrid";
import { FleetMap } from "@/components/FleetMap";
import { ReportButton } from "@/components/ReportButton";
import { SkeletonGrid } from "@/components/SkeletonGrid";
import { SparklineCard } from "@/components/SparklineCard";
import type { Machine } from "@/types/telemetry";

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

export default function DashboardPage() {
  const [machines, setMachines] = useState<Machine[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    telemetryService
      .getFleetStatus()
      .then(setMachines)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Falha ao carregar dados do dashboard.")
      );
  }, []);

  if (error) {
    return (
      <AppShell active="/dashboard" eyebrow="FieldNode" title="Central de Operações">
        <ErrorState title="Dashboard indisponivel" message={error} />
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
          <ReportButton machines={machines ?? []} />
          <div className="inline-flex items-center gap-2 border border-status-normal/20 bg-status-normal/15 px-3 py-1.5 text-xs font-semibold text-status-normal shadow-[0_0_18px_var(--glow-normal)] animate-pulse">
            <span className="h-2.5 w-2.5 bg-status-normal shadow-[0_0_6px_var(--glow-normal-strong)]" />
            Sync offline ativo
          </div>
        </div>
      }
    >
      <p className="mb-8 text-sm text-field-text3">Monitoramento multivariado da frota em tempo real.</p>

      {machines === null ? (
        <SkeletonGrid />
      ) : (
        <div className="space-y-6">
          <section aria-label="Indicadores operacionais" className="grid grid-cols-1 gap-4 sm:gap-6 md:grid-cols-12">
            <div className="md:col-span-4">
              <SparklineCard titulo="RPM Médio" valor={1820} dados={dadosRpm} status="normal" />
            </div>
            <div className="md:col-span-4">
              <SparklineCard
                titulo="Temperatura do Motor"
                valor={78}
                unidade="°C"
                dados={dadosTemperatura}
                status="atencao"
              />
            </div>
            <div className="md:col-span-4">
              <SparklineCard titulo="Vibração do Rotor" valor={2.1} dados={dadosVibracao} status="normal" />
            </div>
          </section>
          <FleetGrid machines={machines} />
          <FleetMap />
          <ChatFAB machines={machines} />
        </div>
      )}
    </AppShell>
  );
}

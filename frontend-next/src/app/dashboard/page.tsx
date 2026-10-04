"use client";

import { useCallback, useEffect, useState } from "react";
import { telemetryService } from "@/services/telemetryService";
import { AppShell } from "@/components/AppShell";
import { ChatFAB } from "@/components/ChatFAB";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/ui/FeedbackStates";
import { FleetGrid } from "@/components/FleetGrid";
import { FleetMap } from "@/components/FleetMap";
import { MetricCard } from "@/components/MetricCard";
import { ReportButton } from "@/components/ReportButton";
import { SkeletonGrid } from "@/components/SkeletonGrid";
import type { Machine, Telemetry } from "@/types/telemetry";

export default function DashboardPage() {
  const [machines, setMachines] = useState<Machine[] | null>(null);
  const [readings, setReadings] = useState<Telemetry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [readingsError, setReadingsError] = useState(false);

  const carregarFrota = useCallback(() => {
    setMachines(null);
    setError(null);
    telemetryService
      .getFleetStatus()
      .then(setMachines)
      .catch((err: unknown) => {
        console.error("[FieldNode] dashboard: falha ao carregar frota", err);
        setError("Não foi possível carregar os dados da frota.");
      });
  }, []);

  const carregarLeituras = useCallback(() => {
    setReadings(null);
    setReadingsError(false);
    telemetryService
      .getLatestReadings()
      .then(setReadings)
      .catch((err: unknown) => {
        console.error(
          "[FieldNode] dashboard: falha ao carregar telemetria",
          err,
        );
        setReadingsError(true);
      });
  }, []);

  useEffect(() => {
    carregarFrota();
    carregarLeituras();
  }, [carregarFrota, carregarLeituras]);

  if (error) {
    return (
      <AppShell
        active="/dashboard"
        eyebrow="FieldNode"
        title="Central de Operações"
      >
        <ErrorState
          title="Dashboard indisponível"
          message={error}
          onRetry={carregarFrota}
        />
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
      <p className="mb-8 text-sm text-field-text3">
        Monitoramento multivariado da frota em tempo real.
      </p>

      {machines === null ? (
        <SkeletonGrid />
      ) : (
        <div className="space-y-6">
          {readings === null ? (
            <LoadingState mensagem="Carregando indicadores de telemetria..." />
          ) : readingsError ? (
            <ErrorState
              title="Indicadores indisponíveis"
              message="Não foi possível carregar as leituras de telemetria."
              onRetry={carregarLeituras}
            />
          ) : readings.length === 0 ? (
            <EmptyState
              title="Nenhuma leitura de telemetria encontrada."
              message="Os indicadores operacionais serão exibidos quando houver leituras disponíveis."
            />
          ) : (
            <section
              aria-label="Indicadores operacionais"
              className="grid grid-cols-1 gap-4 sm:grid-cols-3"
            >
              <MetricCard
                label="RPM médio"
                value={Math.round(
                  readings.reduce((sum, reading) => sum + reading.rpm, 0) /
                    readings.length,
                )}
                helper={`média de ${readings.length} leituras recentes`}
              />
              <MetricCard
                label="Temperatura média"
                value={`${(readings.reduce((sum, reading) => sum + reading.temperatura, 0) / readings.length).toFixed(1)} °C`}
                helper={`média de ${readings.length} leituras recentes`}
                tone="amber"
              />
              <MetricCard
                label="Vibração média"
                value={`${(readings.reduce((sum, reading) => sum + reading.vibracao, 0) / readings.length).toFixed(2)} g`}
                helper={`média de ${readings.length} leituras recentes`}
              />
            </section>
          )}
          <FleetGrid machines={machines} />
          <FleetMap />
          <ChatFAB machines={machines} />
        </div>
      )}
    </AppShell>
  );
}

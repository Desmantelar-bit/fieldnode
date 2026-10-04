"use client";

import { useCallback, useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/ui/FeedbackStates";
import { MetricCard } from "@/components/MetricCard";
import { TelemetryMachineCard } from "@/components/TelemetryMachineCard";
import { telemetryService } from "@/services/telemetryService";
import type { EstadoRequisicao } from "@/types/api";
import type { Telemetry } from "@/types/telemetry";

export default function HarvestersPage() {
  const [estado, setEstado] = useState<EstadoRequisicao<Telemetry[]>>({
    tipo: "carregando",
  });

  const carregar = useCallback(() => {
    setEstado({ tipo: "carregando" });
    telemetryService
      .getLatestReadings()
      .then((data) =>
        setEstado(
          data.length ? { tipo: "sucesso", dados: data } : { tipo: "vazio" },
        ),
      )
      .catch((error: unknown) => {
        console.error(
          "[FieldNode] colheitadeiras: falha ao carregar telemetria",
          error,
        );
        setEstado({
          tipo: "erro",
          mensagem: "Não foi possível carregar as leituras das máquinas.",
        });
      });
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  if (estado.tipo === "carregando") {
    return (
      <AppShell
        active="/colheitadeiras"
        eyebrow="Operacao"
        title="Maquinas agricolas"
      >
        <LoadingState mensagem="Carregando leituras de telemetria..." />
      </AppShell>
    );
  }

  if (estado.tipo === "erro") {
    return (
      <AppShell
        active="/colheitadeiras"
        eyebrow="Operacao"
        title="Maquinas agricolas"
      >
        <ErrorState
          title="Não foi possível carregar as máquinas."
          message={estado.mensagem}
          onRetry={carregar}
        />
      </AppShell>
    );
  }

  if (estado.tipo === "vazio") {
    return (
      <AppShell
        active="/colheitadeiras"
        eyebrow="Operacao"
        title="Maquinas agricolas"
      >
        <EmptyState
          title="Nenhuma leitura encontrada."
          message="Quando a telemetria chegar, as leituras das máquinas aparecerão aqui."
        />
      </AppShell>
    );
  }

  const readings = estado.dados;
  const critical = readings.filter(
    (r) => r.status_risco?.rotuloRisco === "CRITICO",
  ).length;
  const warning = readings.filter(
    (r) => r.status_risco?.rotuloRisco === "ATENCAO",
  ).length;
  const averageTemp =
    readings.reduce((sum, r) => sum + r.temperatura, 0) / readings.length;

  return (
    <AppShell
      active="/colheitadeiras"
      eyebrow="Operacao"
      title="Maquinas agricolas"
    >
      <div className="space-y-5">
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <MetricCard
            label="Monitoradas"
            value={readings.length}
            helper="com leitura recente"
          />
          <MetricCard
            label="Alertas"
            value={critical + warning}
            helper={`${critical} criticos, ${warning} em atencao`}
            tone={critical ? "red" : warning ? "amber" : "emerald"}
          />
          <MetricCard
            label="Temp media"
            value={`${averageTemp.toFixed(1)}C`}
            helper="entre leituras recentes"
            tone="amber"
          />
        </section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {readings.map((reading) => (
            <TelemetryMachineCard key={reading.maquina_id} reading={reading} />
          ))}
        </section>
      </div>
    </AppShell>
  );
}

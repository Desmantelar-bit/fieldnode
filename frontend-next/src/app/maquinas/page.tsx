"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { LoadingState } from "@/components/ui/FeedbackStates";
import { FleetGrid } from "@/components/FleetGrid";
import { telemetryService } from "@/services/telemetryService";
import type { Machine } from "@/types/telemetry";
import type { EstadoRequisicao } from "@/types/api";

export default function MaquinasPage() {
  const [estado, setEstado] = useState<EstadoRequisicao<Machine[]>>({ tipo: 'carregando' });

  const carregar = async () => {
    setEstado({ tipo: 'carregando' });
    try {
      const dados = await telemetryService.getFleetStatus();
      setEstado(dados.length === 0 ? { tipo: 'vazio' } : { tipo: 'sucesso', dados: dados });
    } catch (err) {
      setEstado({ tipo: 'erro', mensagem: err instanceof Error ? err.message : "Falha ao carregar colheitadeiras." });
    }
  };

  useEffect(() => {
    carregar();
  }, []);

  if (estado.tipo === 'carregando') {
    return (
      <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
        <LoadingState mensagem="Carregando frota..." />
      </AppShell>
    );
  }

  if (estado.tipo === 'erro') {
    return (
      <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
        <ErrorState title="Não consegui carregar a frota." message={estado.mensagem} />
      </AppShell>
    );
  }

  if (estado.tipo === 'vazio') {
    return (
      <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
        <EmptyState
          title="Nenhuma máquina cadastrada."
          message="O sistema ainda não tem máquinas registradas. Cadastre na API ou execute o seed inicial."
        />
      </AppShell>
    );
  }

  const machines = estado.dados;

  return (
    <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
      <div className="flex items-center justify-between">
        <p className="text-sm text-field-text3">
          {machines.length} máquina{machines.length !== 1 ? "s" : ""} cadastrada{machines.length !== 1 ? "s" : ""}
        </p>
        <button
          onClick={carregar}
          className="rounded-md border border-field-border bg-field-glass-mid px-3 py-1.5 text-xs font-semibold text-field-text2 transition hover:bg-field-panel2"
        >
          Atualizar
        </button>
      </div>
      <FleetGrid machines={machines} />
    </AppShell>
  );
}

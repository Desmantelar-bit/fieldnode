"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Search } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { LoadingState } from "@/components/ui/FeedbackStates";
import { FleetGrid } from "@/components/FleetGrid";
import { telemetryService } from "@/services/telemetryService";
import type { Machine } from "@/types/telemetry";
import type { EstadoRequisicao } from "@/types/api";

export default function MaquinasPage() {
  const [estado, setEstado] = useState<EstadoRequisicao<Machine[]>>({ tipo: 'carregando' });
  const [busca, setBusca] = useState('');

  const carregar = async () => {
    setEstado({ tipo: 'carregando' });
    try {
      const dados = await telemetryService.getFleetStatus();
      setEstado(dados.length === 0 ? { tipo: 'vazio' } : { tipo: 'sucesso', dados });
    } catch (err) {
      setEstado({ tipo: 'erro', mensagem: err instanceof Error ? err.message : "Falha ao carregar máquinas." });
    }
  };

  useEffect(() => { carregar(); }, []);

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
  const machinesFiltradas = machines.filter((machine) => {
    const query = busca.trim().toLocaleLowerCase();
    if (!query) return true;
    return [machine.maquina_id, machine.modelo.nome, machine.modelo.marca.nome, machine.operario.nome]
      .some((value) => String(value).toLocaleLowerCase().includes(query));
  });

  return (
    <AppShell active="/maquinas" eyebrow="FieldNode" title="Máquinas">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-[var(--text-3)]">
          {machinesFiltradas.length} de {machines.length} máquina{machines.length !== 1 ? "s" : ""}
        </p>
        <div className="flex w-full items-center gap-2 sm:w-auto">
          <label className="relative min-w-0 flex-1 sm:w-64">
            <span className="sr-only">Buscar máquinas</span>
            <Search size={14} aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-3)]" />
            <input value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Buscar ID, modelo ou operador" className="h-10 w-full rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] pl-9 pr-3 text-sm text-[var(--text-1)] outline-none placeholder:text-[var(--text-3)] focus:border-[color:var(--ui-accent)]/60" />
          </label>
          <button type="button" onClick={carregar} aria-label="Atualizar máquinas" title="Atualizar máquinas" className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] text-[var(--text-2)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)] active:scale-95">
            <RefreshCw size={14} aria-hidden="true" />
          </button>
        </div>
      </div>
      {machinesFiltradas.length ? <FleetGrid machines={machinesFiltradas} /> : <EmptyState title="Nenhuma máquina encontrada." message="Ajuste o texto da busca para localizar outra máquina." />}
    </AppShell>
  );
}

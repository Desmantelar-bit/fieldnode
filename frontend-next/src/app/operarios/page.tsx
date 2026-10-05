"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import {
  LoadingState,
  EmptyState,
  ErrorState,
} from "@/components/ui/FeedbackStates";
import { MetricCard } from "@/components/MetricCard";
import { StatusBadge } from "@/components/StatusBadge";
import { telemetryService } from "@/services/telemetryService";
import type { EstadoRequisicao } from "@/types/api";
import type { Operator } from "@/types/telemetry";

export default function OperatorsPage() {
  const [estado, setEstado] = useState<EstadoRequisicao<Operator[]>>({
    tipo: "carregando",
  });

  function carregar() {
    setEstado({ tipo: "carregando" });
    telemetryService
      .getOperators()
      .then((data) =>
        setEstado(
          data.length === 0
            ? { tipo: "vazio" }
            : { tipo: "sucesso", dados: data },
        ),
      )
      .catch((err: unknown) => {
        console.error("[FieldNode] operarios: falha ao carregar lista", err);
        setEstado({
          tipo: "erro",
          mensagem: "Não foi possível carregar a lista de operários.",
        });
      });
  }

  useEffect(() => {
    carregar();
  }, []);

  if (estado.tipo === "carregando") {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operarios">
        <LoadingState mensagem="Carregando operarios..." />
      </AppShell>
    );
  }

  if (estado.tipo === "erro") {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operarios">
        <ErrorState
          title="Não foi possível carregar os operários."
          message={estado.mensagem}
          onRetry={carregar}
        />
      </AppShell>
    );
  }

  if (estado.tipo === "vazio") {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operarios">
        <EmptyState
          title="Nenhum operario cadastrado."
          message="Assim que o backend listar a equipe, os cards aparecem aqui."
        />
      </AppShell>
    );
  }

  const operators = estado.dados;
  const active = operators.filter((o) => o.no_banco).length;
  const averageYears =
    operators.reduce((sum, o) => sum + o.tempo_de_servico, 0) /
    operators.length;

  return (
    <AppShell active="/operarios" eyebrow="Equipe" title="Operarios">
      <div className="space-y-5">
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <MetricCard
            label="Operarios"
            value={operators.length}
            helper="cadastrados"
          />
          <MetricCard
            label="No banco"
            value={active}
            helper={`${operators.length - active} fora do banco`}
            tone="emerald"
          />
          <MetricCard
            label="Tempo medio"
            value={`${averageYears.toFixed(1)} anos`}
            helper="experiencia da equipe"
            tone="amber"
          />
        </section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {operators.map((operator) => (
            <article key={operator.id} className="glass-panel rounded-lg p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex min-w-0 items-center gap-3">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-emerald-300/25 bg-emerald-300/10 text-lg font-semibold text-emerald-100">
                    {operator.nome.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <h2 className="truncate text-base font-semibold text-slate-50">
                      {operator.nome}
                    </h2>
                    <p className="mt-1 text-sm text-slate-400">
                      {operator.tempo_de_servico} anos de servico
                    </p>
                  </div>
                </div>
                <StatusBadge tone={operator.no_banco ? "normal" : "warning"}>
                  {operator.no_banco ? "No banco" : "Fora"}
                </StatusBadge>
              </div>
            </article>
          ))}
        </section>
      </div>
    </AppShell>
  );
}

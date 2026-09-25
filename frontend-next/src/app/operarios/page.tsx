"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { MetricCard } from "@/components/MetricCard";
import { StatusBadge } from "@/components/StatusBadge";
import { telemetryService } from "@/services/telemetryService";
import type { Operator } from "@/types/telemetry";

export default function OperatorsPage() {
  const [operators, setOperators] = useState<Operator[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    telemetryService
      .getOperators()
      .then(setOperators)
      .catch(() => setError("A API de operarios nao respondeu. Parece pouco, mas sem gente no banco a maquina vira enfeite caro."));
  }, []);

  if (error) {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operarios">
        <ErrorState title="Nao consegui carregar os operarios." message={error} />
      </AppShell>
    );
  }

  if (operators === null) {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operarios">
        <div className="animate-pulse text-sm text-field-text3">Carregando...</div>
      </AppShell>
    );
  }

  const active = operators.filter((o) => o.no_banco).length;
  const averageYears = operators.length
    ? operators.reduce((sum, o) => sum + o.tempo_de_servico, 0) / operators.length
    : 0;

  return (
    <AppShell active="/operarios" eyebrow="Equipe" title="Operarios">
      <div className="space-y-5">
        <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <MetricCard label="Operarios" value={operators.length} helper="cadastrados" />
          <MetricCard label="No banco" value={active} helper={`${operators.length - active} fora do banco`} tone="emerald" />
          <MetricCard label="Tempo medio" value={`${averageYears.toFixed(1)} anos`} helper="experiencia da equipe" tone="amber" />
        </section>

        {operators.length === 0 ? (
          <EmptyState title="Nenhum operario cadastrado." message="Assim que o backend listar a equipe, os cards aparecem aqui. Simples, limpo, sem teatro." />
        ) : (
          <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {operators.map((operator) => (
              <article key={operator.id} className="glass-panel rounded-lg p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-emerald-300/25 bg-emerald-300/10 text-lg font-semibold text-emerald-100">
                      {operator.nome.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <h2 className="truncate text-base font-semibold text-slate-50">{operator.nome}</h2>
                      <p className="mt-1 text-sm text-slate-400">{operator.tempo_de_servico} anos de servico</p>
                    </div>
                  </div>
                  <StatusBadge tone={operator.no_banco ? "normal" : "warning"}>{operator.no_banco ? "No banco" : "Fora"}</StatusBadge>
                </div>
              </article>
            ))}
          </section>
        )}
      </div>
    </AppShell>
  );
}

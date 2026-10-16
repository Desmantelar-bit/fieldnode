"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { OperatorDirectory } from '@/components/OperatorDirectory';
import { telemetryService } from '@/services/telemetryService';
import type { Operator } from '@/types/telemetry';

export default function OperatorsPage() {
  const [operators, setOperators] = useState<Operator[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    telemetryService.getOperators()
      .then((data) => {
        if (active) setOperators(data);
      })
      .catch(() => {
        if (active) setError(true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <AppShell
      active="/operarios"
      eyebrow="Equipe"
      title="Operários"
      description="Equipe cadastrada e status de campo"
    >
      {error ? (
        <ErrorState
          title="não conseguimos carregar os operadores."
          message="o serviço de operadores não respondeu no momento. verifique se sua sessão continua ativa e tente novamente."
        />
      ) : loading ? (
        <div className="metric-card animate-pulse py-12 text-center text-sm text-[var(--text-3)]" role="status">
          Carregando equipe…
        </div>
      ) : operators.length === 0 ? (
        <EmptyState
          title="ainda não há operadores cadastrados."
          message="cadastre um operador para incluí-lo na equipe."
        />
      ) : (
        <OperatorDirectory operators={operators} />
      )}
    </AppShell>
  );
}

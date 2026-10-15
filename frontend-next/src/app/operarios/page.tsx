'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { ErrorState } from '@/components/EmptyState';
import { OperatorDirectory } from '@/components/OperatorDirectory';
import { LoadingState } from '@/components/ui/FeedbackStates';
import { telemetryService } from '@/services/telemetryService';
import type { Operator } from '@/types/telemetry';

export default function OperatorsPage() {
  const [operators, setOperators] = useState<Operator[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    telemetryService.getOperators().then((result) => {
      if (active) setOperators(result);
    }).catch(() => {
      if (active) setError(true);
    });
    return () => { active = false; };
  }, []);

  if (error) {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operários">
        <ErrorState
          title="Não consegui carregar os operários."
          message="A API de operários não respondeu. Verifique se o backend está rodando."
        />
      </AppShell>
    );
  }

  if (!operators) {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operários">
        <LoadingState mensagem="Carregando equipe..." />
      </AppShell>
    );
  }

  return (
    <AppShell
      active="/operarios"
      eyebrow="Equipe"
      title="Operários"
      description="Equipe cadastrada e status de campo"
    >
      <OperatorDirectory operators={operators} />
    </AppShell>
  );
}

import { AppShell } from '@/components/AppShell';
import { ErrorState } from '@/components/EmptyState';
import { OperatorDirectory } from '@/components/OperatorDirectory';
import { telemetryService } from '@/services/telemetryService';

export default async function OperatorsPage() {
  let operators;

  try {
    operators = await telemetryService.getOperators();
  } catch {
    return (
      <AppShell active="/operarios" eyebrow="Equipe" title="Operários">
        <ErrorState
          title="não conseguimos carregar os operadores."
          message="o serviço de operadores não respondeu no momento. verifique se o backend está ativo e tente novamente."
        />
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

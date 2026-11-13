import type { ReactNode } from 'react';
import { AlertTriangle, WifiOff } from 'lucide-react';
import { EmptyState, ErrorState } from '@/components/ui/FeedbackStates';
import { SkeletonGrid } from '@/components/SkeletonGrid';
import { SimulatedBadge } from '@/components/SimulatedBadge';

export type DataState = 'loading' | 'ok' | 'sem_historico' | 'desatualizado' | 'offline' | 'erro' | 'invalido';

type Props = {
  state: DataState;
  simulated?: boolean;
  children: ReactNode;
  onRetry?: () => void;
};

export function DataStateBoundary({ state, simulated = false, children, onRetry }: Props) {
  if (state === 'loading') return <SkeletonGrid />;
  if (state === 'sem_historico') {
    return <EmptyState title="Sem histórico suficiente" message="Aguardando leituras para apresentar este indicador." />;
  }
  if (state === 'offline') {
    return (
      <section role="status" className="metric-card flex items-center justify-between gap-3 border border-[color:var(--status-atencao)]/30">
        <p className="flex items-center gap-2 text-sm text-[var(--text-1)]"><WifiOff size={16} aria-hidden="true" />Sem conexão com a API.</p>
        {onRetry && <button type="button" onClick={onRetry} className="rounded-lg px-3 py-2 text-xs font-semibold text-[var(--text-1)]">Tentar novamente</button>}
      </section>
    );
  }
  if (state === 'erro') return <ErrorState title="Falha ao carregar dados" message="A API não conseguiu fornecer os dados agora." onRetry={onRetry} />;
  if (state === 'invalido') return <ErrorState title="Resposta inválida" message="Os dados recebidos não correspondem ao contrato esperado." />;

  return (
    <div>
      {simulated && <SimulatedBadge />}
      {children}
      {state === 'desatualizado' && (
        <p role="status" className="mt-3 flex items-center gap-2 rounded-xl border border-[color:var(--status-atencao)]/30 bg-[color:var(--status-atencao)]/5 p-3 text-xs text-[var(--text-1)]">
          <AlertTriangle size={15} aria-hidden="true" />Último dado conhecido; a atualização está atrasada.
        </p>
      )}
    </div>
  );
}

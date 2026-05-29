import type { Machine } from '@/types/telemetry';
import { EmptyState } from '@/components/EmptyState';
import { StatusBadge } from '@/components/StatusBadge';

export function FleetGrid({ machines }: { machines: Machine[] }) {
  if (machines.length === 0) {
    return <EmptyState title="Nenhuma colheitadeira cadastrada ainda." message="Assim que a API listar maquinas, elas aparecem aqui. Por enquanto, o campo esta quieto demais." />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {machines.map((machine) => (
        <article key={machine.id} className="glass-panel rounded-lg p-4 transition hover:border-emerald-200/30 hover:bg-white/[0.055] sm:p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="truncate text-base font-semibold text-slate-50 sm:text-lg">{machine.modelo.nome}</h3>
              <p className="text-sm text-slate-400">{machine.modelo.marca.nome}</p>
            </div>
            <StatusBadge tone={machine.status_de_operacao.em_operacao ? 'normal' : 'muted'}>{machine.status_de_operacao.em_operacao ? 'Ativo' : 'Inativo'}</StatusBadge>
          </div>

          <dl className="mt-5 grid grid-cols-1 gap-3 text-sm text-slate-400 min-[420px]:grid-cols-2">
            <div className="rounded-md border border-white/10 bg-white/[0.035] p-3">
              <dt>Operario</dt>
              <dd className="mt-1 truncate font-semibold text-slate-50">{machine.operario.nome}</dd>
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.035] p-3">
              <dt>Velocidade</dt>
              <dd className="mt-1 font-semibold text-slate-50">{machine.estado_de_movimento.velocidade} km/h</dd>
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.035] p-3">
              <dt>Movimento</dt>
              <dd className="mt-1 font-semibold text-slate-50">{machine.estado_de_movimento.em_movimento ? 'Em campo' : 'Parada'}</dd>
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.035] p-3">
              <dt>Horas</dt>
              <dd className="mt-1 font-semibold text-slate-50">{machine.status_de_operacao.tempo_de_operacao}h</dd>
            </div>
          </dl>

          {/* Botão para ver prescrições */}
          <div className="mt-4">
            <a
              href={`/maquinas/${machine.id}/prescricao`}
              className="w-full inline-flex items-center justify-center px-3 py-2 bg-emerald-600/10 border border-emerald-500/20 text-sm font-medium text-emerald-100 hover:bg-emerald-600/20 hover:border-emerald-500/30 transition-colors rounded-md"
            >
              Ver Prescrição
            </a>
          </div>
        </article>
      ))}
    </div>
  );
}

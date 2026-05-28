import type { Machine } from '@/types/telemetry';

export function FleetGrid({ machines }: { machines: Machine[] }) {
  if (machines.length === 0) {
    return (
      <section className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-center sm:p-10">
        <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">Sem dados</p>
        <h2 className="mt-2 text-xl font-bold text-slate-950">Nenhuma colheitadeira cadastrada ainda.</h2>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-600">
          Assim que a API receber ou listar maquinas, elas aparecem aqui. Por enquanto, o campo esta quieto demais.
        </p>
      </section>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {machines.map((machine) => (
        <article key={machine.id} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:border-slate-300 sm:p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="truncate text-base font-bold text-slate-950 sm:text-lg">{machine.modelo.nome}</h3>
              <p className="text-sm text-slate-500">{machine.modelo.marca.nome}</p>
            </div>
            <span className={`shrink-0 rounded px-2 py-1 text-xs font-semibold ${machine.status_de_operacao.em_operacao ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>
              {machine.status_de_operacao.em_operacao ? 'ATIVO' : 'INATIVO'}
            </span>
          </div>

          <dl className="mt-5 grid grid-cols-1 gap-3 text-sm text-slate-600 min-[420px]:grid-cols-2">
            <div className="rounded-md bg-slate-50 p-3">
              <dt>Operario</dt>
              <dd className="mt-1 truncate font-semibold text-slate-950">{machine.operario.nome}</dd>
            </div>
            <div className="rounded-md bg-slate-50 p-3">
              <dt>Velocidade</dt>
              <dd className="mt-1 font-semibold text-slate-950">{machine.estado_de_movimento.velocidade} km/h</dd>
            </div>
            <div className="rounded-md bg-slate-50 p-3">
              <dt>Movimento</dt>
              <dd className="mt-1 font-semibold text-slate-950">{machine.estado_de_movimento.em_movimento ? 'Em campo' : 'Parada'}</dd>
            </div>
            <div className="rounded-md bg-slate-50 p-3">
              <dt>Horas</dt>
              <dd className="mt-1 font-semibold text-slate-950">{machine.status_de_operacao.tempo_de_operacao}h</dd>
            </div>
          </dl>
        </article>
      ))}
    </div>
  );
}

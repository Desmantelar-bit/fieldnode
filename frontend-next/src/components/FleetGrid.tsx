import { Machine } from '@/types/telemetry';

export function FleetGrid({ machines }: { machines: Machine[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {machines.map((machine) => (
        <div key={machine.id} className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-900">{machine.modelo.nome}</h3>
              <p className="text-sm text-slate-500">{machine.modelo.marca.nome}</p>
            </div>
            <span className={`px-2 py-1 rounded text-xs font-medium ${machine.status_de_operacao.em_operacao ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
              {machine.status_de_operacao.em_operacao ? 'ATIVO' : 'INATIVO'}
            </span>
          </div>
          <div className="space-y-2 text-sm text-slate-600">
            <p className="flex justify-between"><span>Operário:</span> <span className="font-medium text-slate-900">{machine.operario.nome}</span></p>
            <p className="flex justify-between"><span>Velocidade:</span> <span className="font-medium text-slate-900">{machine.estado_de_movimento.velocidade} km/h</span></p>
          </div>
        </div>
      ))}
    </div>
  );
}
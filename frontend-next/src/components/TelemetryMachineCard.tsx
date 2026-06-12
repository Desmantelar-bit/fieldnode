import Link from 'next/link';
import type { Telemetry } from '@/types/telemetry';
import { riskTone, StatusBadge } from '@/components/StatusBadge';
import { PrescricaoButton } from '@/components/PrescricaoButton';

function metricTone(value: number, warning: number, critical: number, reverse = false) {
  if (reverse) return value < critical ? 'text-amber-200' : 'text-emerald-200';
  if (value > critical) return 'text-red-200';
  if (value > warning) return 'text-amber-200';
  return 'text-emerald-200';
}

function machineKind(id: string) {
  if (id.startsWith('TRAT')) return 'Trator';
  if (id.startsWith('PULV')) return 'Pulverizador';
  if (id.startsWith('PLAN')) return 'Plantadeira';
  return 'Colheitadeira';
}

export function TelemetryMachineCard({ reading }: { reading: Telemetry }) {
  return (
    <div className="glass-panel block rounded-lg p-5 transition hover:border-emerald-200/30 hover:bg-white/[0.055] min-h-[4rem]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">
            {machineKind(reading.maquina_id)}
          </p>
          <h2 className="mt-2 truncate font-mono text-lg font-semibold text-slate-50">
            {reading.maquina_id}
          </h2>
        </div>
        <StatusBadge tone={riskTone(reading.nivel_risco)}>
          {reading.nivel_risco || "NORMAL"}
        </StatusBadge>
      </div>

      <dl className="mt-5 grid grid-cols-3 gap-3">
        <div>
          <dt className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
            Temp
          </dt>
          <dd
            className={`mt-1 text-base font-semibold ${metricTone(reading.temperatura, 75, 85)}`}
          >
            {reading.temperatura}C
          </dd>
        </div>
        <div>
          <dt className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
            Vib
          </dt>
          <dd
            className={`mt-1 text-base font-semibold ${metricTone(reading.vibracao, 0.5, 0.8)}`}
          >
            {reading.vibracao}g
          </dd>
        </div>
        <div>
          <dt className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
            RPM
          </dt>
          <dd
            className={`mt-1 text-base font-semibold ${metricTone(reading.rpm, 0, 1300, true)}`}
          >
            {reading.rpm}
          </dd>
        </div>
      </dl>

      <div className="mt-4 flex gap-2">
        <Link
          href={`/detalhes?id=${encodeURIComponent(reading.maquina_id)}`}
          className="flex-1 rounded-md bg-emerald-900/30 px-3 py-2 text-xs font-semibold text-emerald-200 transition hover:bg-emerald-900/50"
        >
          Ver Detalhes
        </Link>
        <PrescricaoButton machineId={reading.maquina_id} />
      </div>
    </div>
  );
}

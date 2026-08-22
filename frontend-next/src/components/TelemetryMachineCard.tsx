import Link from 'next/link';
import type { Telemetry } from '@/types/telemetry';
import { riskTone, StatusBadge } from '@/components/StatusBadge';
import { PrescricaoButton } from '@/components/PrescricaoButton';

function metricTone(value: number, warning: number, critical: number, reverse = false) {
  if (reverse) return value < critical ? 'text-status-atencao' : 'text-status-normal';
  if (value > critical) return 'text-status-critico';
  if (value > warning) return 'text-status-atencao';
  return 'text-status-normal';
}

function machineKind(id: string) {
  if (id.startsWith('TRAT')) return 'Trator';
  if (id.startsWith('PULV')) return 'Pulverizador';
  if (id.startsWith('PLAN')) return 'Plantadeira';
  return 'Colheitadeira';
}

function riskLabel(reading: Telemetry) {
  return reading.status_risco?.rotuloRisco || 'NORMAL';
}

export function TelemetryMachineCard({ reading }: { reading: Telemetry }) {
  const risk = riskLabel(reading);

  return (
    <div className="glass-panel block rounded-lg p-6 transition hover:border-accent/30 hover:bg-field-glass-strong min-h-[4rem]">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-label text-field-text3">
            {machineKind(reading.maquina_id)}
          </p>
          <h2 className="mt-2 truncate font-mono text-lg font-semibold text-field-text1">
            {reading.maquina_id}
          </h2>
        </div>
        <StatusBadge tone={riskTone(risk)}>
          {risk}
        </StatusBadge>
      </div>

      <dl className="mt-6 grid grid-cols-3 gap-3">
        <div>
          <dt className="text-[10px] font-semibold uppercase tracking-label text-field-text3">
            Temp
          </dt>
          <dd className={`mt-1 text-base font-semibold ${metricTone(reading.temperatura, 75, 85)}`}>
            {reading.temperatura}C
          </dd>
        </div>
        <div>
          <dt className="text-[10px] font-semibold uppercase tracking-label text-field-text3">
            Vib
          </dt>
          <dd className={`mt-1 text-base font-semibold ${metricTone(reading.vibracao, 0.5, 0.8)}`}>
            {reading.vibracao}g
          </dd>
        </div>
        <div>
          <dt className="text-[10px] font-semibold uppercase tracking-label text-field-text3">
            RPM
          </dt>
          <dd className={`mt-1 text-base font-semibold ${metricTone(reading.rpm, 0, 1300, true)}`}>
            {reading.rpm}
          </dd>
        </div>
      </dl>

      <div className="mt-4 flex gap-2">
        <Link
          href={`/detalhes?id=${encodeURIComponent(reading.maquina_id)}`}
          className="flex-1 rounded-md bg-accent/10 px-3 py-2 text-xs font-semibold text-accent transition hover:bg-accent/20"
        >
          Ver Detalhes
        </Link>
        <PrescricaoButton machineId={reading.maquina_id} />
      </div>
    </div>
  );
}

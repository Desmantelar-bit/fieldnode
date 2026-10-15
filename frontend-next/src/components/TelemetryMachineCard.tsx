import Link from 'next/link';
import type { Telemetry } from '@/types/telemetry';
import { riskTone, StatusBadge } from '@/components/StatusBadge';
import { PrescricaoButton } from '@/components/PrescricaoButton';
import { Thermometer, Vibrate, Gauge } from 'lucide-react';

function metricTone(value: number, warning: number, critical: number, reverse = false) {
  if (reverse) return value < critical ? 'text-[color:var(--status-atencao)]' : 'text-[color:var(--status-normal)]';
  if (value > critical) return 'text-[color:var(--status-critico)]';
  if (value > warning)  return 'text-[color:var(--status-atencao)]';
  return 'text-[color:var(--status-normal)]';
}

function machineKind(id: string) {
  if (id.startsWith('TRAT')) return 'Trator';
  if (id.startsWith('PULV')) return 'Pulverizador';
  if (id.startsWith('PLAN')) return 'Plantadeira';
  return 'Colheitadeira';
}

function riskLabel(reading: Telemetry) {
  const rotulo = reading.status_risco?.rotuloRisco?.trim();
  if (!rotulo) return 'NORMAL';
  const normalized = rotulo
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase();
  if (normalized === 'ATENCAO' || normalized === 'ALERTA') return 'ALERTA';
  if (normalized === 'CRITICO') return 'CRÍTICO';
  return rotulo.toUpperCase();
}

export function TelemetryMachineCard({ reading }: { reading: Telemetry }) {
  const risk = riskLabel(reading);

  return (
    <article className="metric-card transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[var(--shadow-glass)]">
      {/* Cabeçalho */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
            {machineKind(reading.maquina_id)}
          </p>
          <h2 className="mt-1 truncate font-mono text-base font-bold text-[var(--text-1)]">
            {reading.maquina_id}
          </h2>
        </div>
        <StatusBadge tone={riskTone(risk)}>{risk}</StatusBadge>
      </div>

      {/* Métricas */}
      <dl className="mt-5 grid grid-cols-3 gap-2">
        <div className="data-tile p-3">
          <dt className="flex items-center gap-1 text-[9px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
            <Thermometer size={10} aria-hidden="true" />
            Temp
          </dt>
          <dd className={`mt-1.5 text-sm font-bold ${metricTone(reading.temperatura, 75, 85)}`}>
            {reading.temperatura}°C
          </dd>
        </div>
        <div className="data-tile p-3">
          <dt className="flex items-center gap-1 text-[9px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
            <Vibrate size={10} aria-hidden="true" />
            Vib
          </dt>
          <dd className={`mt-1.5 text-sm font-bold ${metricTone(reading.vibracao, 0.5, 0.8)}`}>
            {reading.vibracao}g
          </dd>
        </div>
        <div className="data-tile p-3">
          <dt className="flex items-center gap-1 text-[9px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
            <Gauge size={10} aria-hidden="true" />
            RPM
          </dt>
          <dd className={`mt-1.5 text-sm font-bold ${metricTone(reading.rpm, 0, 1300, true)}`}>
            {reading.rpm}
          </dd>
        </div>
      </dl>

      {/* Ações */}
      <div className="mt-4 flex gap-2">
        <Link
          href={`/detalhes?id=${encodeURIComponent(reading.maquina_id)}`}
          className="flex-1 rounded-xl bg-[var(--panel-glass-mid)] px-3 py-2 text-center text-xs font-semibold text-[var(--text-2)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)]"
        >
          Detalhes
        </Link>
        <PrescricaoButton machineId={reading.maquina_id} />
      </div>
    </article>
  );
}

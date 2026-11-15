'use client';

import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CircleHelp } from 'lucide-react';
import { getFleetHeatmap } from '@/services/heatmapService';
import type { Heatmap, HeatmapCell } from '@/schemas/heatmap';

const tone: Record<string, string> = { NORMAL: 'heat-cell--normal', ATENCAO: 'heat-cell--attention', CRITICO: 'heat-cell--critical' };
const severityLabel: Record<string, string> = { NORMAL: 'normal', ATENCAO: 'atenção', CRITICO: 'crítica' };

export function HeatGrid() {
  const [data, setData] = useState<Heatmap | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { const controller = new AbortController(); getFleetHeatmap(controller.signal).then(setData).catch((err) => { if (!controller.signal.aborted) setError(err instanceof Error ? err.message : 'Não foi possível carregar o grid.'); }); return () => controller.abort(); }, []);

  const hours = useMemo(() => data ? [...new Set(data.results.map((cell) => cell.hour))].sort() : [], [data]);
  const machines = useMemo(() => data ? [...new Map(data.results.map((cell) => [cell.machine_id, cell.machine_external_code])).entries()] : [], [data]);
  const cellMap = useMemo(() => new Map(data?.results.map((cell) => [`${cell.machine_id}|${cell.hour}`, cell]) ?? []), [data]);
  function renderCell(cell: HeatmapCell | undefined, machine: string, hour: string) {
    const label = cell ? `${machine}, ${new Date(hour).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}. Pior severidade ${severityLabel[cell.worst_severity]}. ${cell.event_count} evento(s).${cell.quality_issue ? ' Qualidade do dado requer verificação.' : ' Qualidade sem alerta registrado.'}` : `${machine}, ${new Date(hour).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}. Sem eventos registrados.`;
    return <div role="gridcell" aria-label={label} title={label} className={`heat-cell ${cell ? tone[cell.worst_severity] : 'heat-cell--empty'} ${cell?.quality_issue ? 'heat-cell--quality' : ''}`}>{cell?.quality_issue ? <AlertTriangle size={12} aria-hidden="true" /> : null}</div>;
  }
  return <section aria-labelledby="heat-grid-title" className="heat-grid-panel">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="section-heading">Padrão temporal</p><h2 id="heat-grid-title" className="mt-1 text-lg font-semibold text-[var(--text-1)]">Severidade da frota por hora</h2><p className="mt-1 text-xs text-[var(--text-3)]">Agregado no banco por <code>event_time</code>. Células vazias não significam normalidade.</p></div><span className="rounded-lg p-1.5 text-[var(--text-3)]" title="A cor indica severidade; o ícone indica qualidade insuficiente."><CircleHelp size={16} aria-hidden="true" /></span></div>
    {error ? <p role="alert" className="mt-5 text-sm text-[color:var(--status-critico)]">{error}</p> : !data ? <p role="status" className="mt-5 text-sm text-[var(--text-3)]">Carregando histórico horário…</p> : !data.results.length ? <p className="mt-5 text-sm text-[var(--text-3)]">Sem eventos com horário confiável no período consultado.</p> : <>
      <div className="mt-5 overflow-x-auto" role="grid" aria-label="Grid de severidade da frota por hora"><div className="heat-grid" style={{ gridTemplateColumns: `minmax(7rem, 9rem) repeat(${hours.length}, minmax(3.2rem, 1fr))` }}><div className="heat-grid-corner">Máquina</div>{hours.map((hour) => <div key={hour} className="heat-grid-hour">{new Date(hour).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</div>)}{machines.map(([machineId, machine]) => <div key={machineId} className="contents"><div className="heat-grid-machine">{machine}</div>{hours.map((hour) => renderCell(cellMap.get(`${machineId}|${hour}`), machine, hour))}</div>)}</div></div>
      <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-[11px] text-[var(--text-2)]" aria-label="Legenda do grid"><span><i className="heat-legend heat-cell--normal" /> Normal</span><span><i className="heat-legend heat-cell--attention" /> Atenção</span><span><i className="heat-legend heat-cell--critical" /> Crítica</span><span><i className="heat-legend heat-cell--empty" /> Sem eventos</span><span><AlertTriangle size={12} aria-hidden="true" /> qualidade a verificar</span></div>
    </>}
  </section>;
}

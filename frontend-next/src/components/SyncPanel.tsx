'use client';

import { useEffect, useMemo, useState } from 'react';

type DeviceReport = {
  device_id: string;
  ultimo_ack: number;
  pendentes_por_classe: Record<'A' | 'B' | 'C', number>;
  backlog: number;
  atraso_maximo_segundos: number | null;
};
type QueueItem = { device_id?: string; priority_class?: 'A' | 'B' | 'C'; state?: string; createdAt?: string };
type SyncResponse = {
  sincronizacao?: { dispositivos?: DeviceReport[]; perdas_registradas?: number; backlog_total?: number; alerta_backlog?: boolean };
};

const EMPTY_CLASSES = { A: 0, B: 0, C: 0 } as const;

export function SyncPanel() {
  const [report, setReport] = useState<SyncResponse['sincronizacao']>();
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await fetch('/api/status-mqtt/', { cache: 'no-store' });
        if (!response.ok) throw new Error('status unavailable');
        const data: SyncResponse = await response.json();
        if (active) { setReport(data.sincronizacao); setError(false); }
      } catch { if (active) setError(true); }
    };
    const onQueue = (event: Event) => {
      const detail = (event as CustomEvent<{ items?: QueueItem[] }>).detail;
      if (detail?.items) setQueue(detail.items.filter((item) => item.state !== 'SINCRONIZADA'));
    };
    load();
    const id = window.setInterval(load, 15000);
    window.addEventListener('fieldnode-queue-status', onQueue);
    navigator.serviceWorker?.controller?.postMessage({ type: 'GET_TELEMETRY_STATUS' });
    return () => { active = false; window.clearInterval(id); window.removeEventListener('fieldnode-queue-status', onQueue); };
  }, []);

  const local = useMemo(() => queue.reduce((acc, item) => {
    const priority = item.priority_class || 'C';
    acc[priority] += 1;
    return acc;
  }, { ...EMPTY_CLASSES }), [queue]);
  const devices = report?.dispositivos || [];
  const hasAlert = Boolean(report?.alerta_backlog || queue.length || report?.perdas_registradas);

  return (
    <section aria-labelledby="sync-panel-title" className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="section-heading" id="sync-panel-title">Sincronização</p>
          <p className="mt-1 text-xs text-[var(--text-3)]">ACK, backlog local e falhas registradas. Dado parado ainda é dado, mas precisa estar etiquetado.</p>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] ${hasAlert ? 'bg-[color:var(--status-atencao)]/15 text-[color:var(--status-atencao)]' : 'bg-[color:var(--status-normal)]/15 text-[color:var(--status-normal)]'}`} role="status">
          {hasAlert ? 'Atenção' : 'Em dia'}
        </span>
      </div>
      {error ? <p className="mt-4 text-sm text-[color:var(--status-atencao)]" role="alert">Relatório de sincronização indisponível.</p> : (
        <>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            {(['A', 'B', 'C'] as const).map((priority) => <div key={priority} className="rounded-xl border border-[var(--line)] p-3"><p className="text-[10px] uppercase tracking-[0.1em] text-[var(--text-3)]">Pendentes classe {priority}</p><p className="mt-1 text-2xl font-semibold text-[var(--text-1)]">{local[priority] + devices.reduce((sum, device) => sum + (device.pendentes_por_classe?.[priority] || 0), 0)}</p></div>)}
          </div>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-xs"><caption className="sr-only">Estado de sincronização por dispositivo</caption><thead className="text-[10px] uppercase tracking-[0.08em] text-[var(--text-3)]"><tr><th className="pb-2">Dispositivo</th><th className="pb-2">Último ACK</th><th className="pb-2">Backlog</th><th className="pb-2">Atraso máximo</th></tr></thead><tbody>{devices.map((device) => <tr key={device.device_id} className="border-t border-[var(--line)]"><td className="py-2 font-medium">{device.device_id}</td><td className="py-2">seq. {device.ultimo_ack}</td><td className="py-2">{device.backlog}</td><td className="py-2">{device.atraso_maximo_segundos == null ? 'n/d' : `${device.atraso_maximo_segundos}s`}</td></tr>)}</tbody></table>
          </div>
          <p className={`mt-4 text-xs ${report?.perdas_registradas ? 'text-[color:var(--status-critico)]' : 'text-[var(--text-3)]'}`} role={report?.perdas_registradas ? 'alert' : undefined}>Perdas registradas: {report?.perdas_registradas || 0}. Fila local: A {local.A}, B {local.B}, C {local.C}.</p>
        </>
      )}
    </section>
  );
}

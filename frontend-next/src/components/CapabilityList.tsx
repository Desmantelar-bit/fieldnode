'use client';

import { useEffect, useState } from 'react';
import { telemetryService } from '@/services/telemetryService';
import type { MachineCapability } from '@/schemas/capabilities';

export function CapabilityList({ machineId }: { machineId: string }) {
  const [items, setItems] = useState<MachineCapability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    telemetryService.getMachineCapabilities(machineId, controller.signal)
      .then((data) => setItems(data.capabilities))
      .catch(() => { if (!controller.signal.aborted) setError(true); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [machineId]);

  return (
    <section aria-label="Capacidades informadas pela máquina" className="metric-card">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]">O que esta máquina informa</p>
          <h2 className="mt-0.5 text-sm font-semibold text-[var(--text-1)]">Capacidade observada</h2>
        </div>
        <span className="text-[11px] text-[var(--text-3)]">últimos 7 dias</span>
      </div>
      {loading ? <p className="mt-4 text-xs text-[var(--text-3)]">Lendo capacidades observadas...</p> : null}
      {error ? <p className="mt-4 text-xs text-[var(--text-3)]">Não foi possível consultar as capacidades desta máquina.</p> : null}
      {!loading && !error && items.length === 0 ? <p className="mt-4 text-xs text-[var(--text-3)]">Nenhum parâmetro informado no período. Ausência não significa zero.</p> : null}
      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {items.map((item) => (
          <div key={item.canonical_parameter} className="data-tile rounded-xl p-3">
            <div className="flex items-baseline justify-between gap-2">
              <p className="truncate text-sm font-semibold text-[var(--text-1)]">{item.canonical_parameter}</p>
              <span className="text-[10px] text-[var(--text-3)]">{item.unidade ?? 'unidade não informada'}</span>
            </div>
            <p className="mt-1 text-[11px] text-[var(--text-2)]">{item.fonte.protocol} · {item.qualidade}</p>
            <p className="mt-1 text-[10px] text-[var(--text-3)]">{item.taxa_media_por_hora == null ? 'taxa insuficiente para estimar' : `${item.taxa_media_por_hora}/h`} · {item.amostras} amostras</p>
          </div>
        ))}
      </div>
    </section>
  );
}

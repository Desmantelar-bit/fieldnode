'use client';

import { useMemo, useState, type MouseEvent } from 'react';
import { resolveApiUrl } from '@/services/telemetryService';

type ReportMachineOption = {
  maquina_id?: string | null;
  modelo?: {
    nome?: string;
  };
};

type ReportButtonProps = {
  machineId?: string;
  machines?: ReportMachineOption[];
  label?: string;
  className?: string;
};

export function ReportButton({ machineId, machines = [], label = 'Extrair relatorio', className = '' }: ReportButtonProps) {
  const machineOptions = useMemo(
    () => machines.filter((machine) => machine.maquina_id),
    [machines]
  );
  const [selectedMachineId, setSelectedMachineId] = useState(machineOptions[0]?.maquina_id ?? '');
  const exportMachineId = machineId || selectedMachineId;

  const handleClick = async (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!exportMachineId) {
      alert('Selecione uma maquina para gerar o relatorio.');
      return;
    }

    const url = `${resolveApiUrl()}/relatorio/exportar/?maquina_id=${encodeURIComponent(exportMachineId)}`;

    try {
      const res = await fetch(url, { headers: { Accept: '*/*' } });
      if (!res.ok) throw new Error(String(res.status));

      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = blobUrl;
      anchor.download = `relatorio_${exportMachineId}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(blobUrl), 0);
    } catch {
      alert('Nao foi possivel gerar o relatorio agora.');
    }
  };

  if (!machineId && machineOptions.length > 0) {
    return (
      <div className="flex items-center gap-2">
        <select
          value={selectedMachineId}
          onChange={(event) => setSelectedMachineId(event.target.value)}
          className="border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 outline-none transition hover:bg-white/[0.08] focus:border-emerald-300/50"
          aria-label="Maquina do relatorio"
        >
          {machineOptions.map((machine) => (
            <option key={machine.maquina_id} value={machine.maquina_id ?? ''}>
              {machine.maquina_id} {machine.modelo?.nome ? `- ${machine.modelo.nome}` : ''}
            </option>
          ))}
        </select>
        <button
          onClick={handleClick}
          className={[
            'border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]',
            className,
          ].join(' ')}
        >
          {label}
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={handleClick}
      className={[
        'border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]',
        className,
      ].join(' ')}
    >
      {label}
    </button>
  );
}

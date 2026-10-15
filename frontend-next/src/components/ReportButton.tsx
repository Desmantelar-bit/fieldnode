'use client';

import { useMemo, useState, type MouseEvent } from 'react';
import { Download } from 'lucide-react';
import { resolveApiUrl } from '@/services/telemetryService';
import { handleUnauthorizedResponse } from '@/services/authService';

type ReportMachineOption = {
  maquina_id?: string | null;
  modelo?: { nome?: string };
};

type ReportButtonProps = {
  machineId?: string;
  machines?: ReportMachineOption[];
  label?: string;
  className?: string;
};

const selectClass =
  'rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] px-3 py-2 text-xs font-semibold text-[var(--text-1)] outline-none transition hover:border-[color:var(--ui-accent)]/40 focus:border-[color:var(--ui-accent)]/60';

const btnClass =
  'inline-flex shrink-0 items-center gap-1.5 rounded-xl bg-[var(--panel-glass-mid)] px-3 py-2 text-xs font-semibold text-[var(--text-2)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)] active:scale-95';

function ExportButton({
  onClick,
  label,
  className,
}: {
  onClick: (e: MouseEvent<HTMLButtonElement>) => void;
  label: string;
  className: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`${btnClass} ${className}`}
      aria-label={label}
      title={label}
    >
      <Download size={13} aria-hidden="true" />
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
}

export function ReportButton({
  machineId,
  machines = [],
  label = 'Exportar',
  className = '',
}: ReportButtonProps) {
  const machineOptions = useMemo(
    () => machines.filter((m) => m.maquina_id),
    [machines],
  );
  const [selectedMachineId, setSelectedMachineId] = useState(
    machineOptions[0]?.maquina_id ?? '',
  );
  const exportMachineId = machineId || selectedMachineId;

  const handleClick = async (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!exportMachineId) {
      alert('Selecione uma máquina para gerar o relatório.');
      return;
    }
    const url = `${resolveApiUrl()}/relatorio/exportar/?maquina_id=${encodeURIComponent(exportMachineId)}`;
    try {
      const headers = new Headers({ Accept: '*/*' });
      if (typeof window !== 'undefined') {
        try {
          const token = localStorage.getItem('fn-auth-token');
          if (token) headers.set('Authorization', `Token ${token}`);
        } catch {
          // storage unavailable
        }
      }
      const res = await fetch(url, { headers });
      handleUnauthorizedResponse(res);
      if (res.status === 404 || res.status === 501) {
        alert('O serviço de exportação de relatório (/api/relatorio/exportar/) ainda não está habilitado no backend.');
        return;
      }
      if (!res.ok) throw new Error(String(res.status));
      const blob    = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const anchor  = document.createElement('a');
      anchor.href     = blobUrl;
      anchor.download = `relatorio_${exportMachineId}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(blobUrl), 0);
    } catch {
      alert('Não foi possível gerar o relatório agora.');
    }
  };

  if (!machineId && machineOptions.length > 0) {
    return (
      <div className="flex min-w-0 items-center gap-2">
        <select
          value={selectedMachineId}
          onChange={(e) => setSelectedMachineId(e.target.value)}
          className={`${selectClass} min-w-0 max-w-[11rem] sm:max-w-none`}
          aria-label="Máquina do relatório"
        >
          {machineOptions.map((m) => (
            <option key={m.maquina_id} value={m.maquina_id ?? ''}>
              {m.maquina_id} {m.modelo?.nome ? `· ${m.modelo.nome}` : ''}
            </option>
          ))}
        </select>
        <ExportButton onClick={handleClick} label={label} className={className} />
      </div>
    );
  }

  return <ExportButton onClick={handleClick} label={label} className={className} />;
}

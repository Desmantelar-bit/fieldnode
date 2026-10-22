'use client';

import { useCallback, useMemo, useState, type MouseEvent } from 'react';
import { Download, LoaderCircle } from 'lucide-react';
import { telemetryService } from '@/services/telemetryService';

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
  loading,
}: {
  onClick: (e: MouseEvent<HTMLButtonElement>) => void;
  label: string;
  className: string;
  loading: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`${btnClass} ${className}`}
      aria-label={label}
      title={label}
      disabled={loading}
      aria-busy={loading}
    >
      {loading ? <LoaderCircle size={13} className="animate-spin" aria-hidden="true" /> : <Download size={13} aria-hidden="true" />}
      <span className="hidden sm:inline">{loading ? 'Gerando…' : label}</span>
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
  const [exporting, setExporting] = useState(false);
  const exportMachineId = machineId || selectedMachineId;

  const handleExport = useCallback(
    async (e?: MouseEvent<HTMLButtonElement>) => {
      e?.preventDefault();
      if (!exportMachineId) {
        alert('Selecione uma máquina para gerar o relatório.');
        return;
      }
      if (exporting) return;
      setExporting(true);
      try {
        const blob = await telemetryService.exportReport(exportMachineId);
        const blobUrl = window.URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = blobUrl;
        anchor.download = `relatorio_${exportMachineId}_${new Date().toISOString().slice(0, 10)}.xlsx`;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        window.setTimeout(() => window.URL.revokeObjectURL(blobUrl), 0);
      } catch {
        alert('Não foi possível gerar o relatório agora.');
      } finally {
        setExporting(false);
      }
    },
    [exportMachineId, exporting],
  );

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
        <ExportButton onClick={handleExport} label={label} className={className} loading={exporting} />
      </div>
    );
  }

  return <ExportButton onClick={handleExport} label={label} className={className} loading={exporting} />;
}

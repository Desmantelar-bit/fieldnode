'use client';

import type { MouseEvent } from 'react';

type ReportButtonProps = {
  machineId?: string;
  label?: string;
  className?: string;
};

export function ReportButton({ machineId, label = 'Extrair relatorio', className = '' }: ReportButtonProps) {
  const handleClick = async (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const baseUrl = typeof window !== 'undefined'
      ? (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api')
      : '/api';

    let url: string;
    if (machineId) {
      url = `${baseUrl}/relatorio/exportar/?maquina_id=${encodeURIComponent(machineId)}`;
    } else {
      url = `${baseUrl}/relatorio/?formato=csv`;
    }

    try {
      const res = await fetch(url, { headers: { Accept: 'text/csv' } });
      if (!res.ok) throw new Error(String(res.status));

      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = blobUrl;
      anchor.download = machineId
        ? `relatorio_${machineId}_${new Date().toISOString().slice(0, 10)}.csv`
        : `relatorio_geral_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(blobUrl), 0);
    } catch {
      alert('Nao foi possivel gerar o relatorio agora.');
    }
  };

  return (
    <button
      onClick={handleClick}
      className={[
        'rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]',
        className,
      ].join(' ')}
    >
      {label}
    </button>
  );
}

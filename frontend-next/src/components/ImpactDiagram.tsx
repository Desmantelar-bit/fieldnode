'use client';

export type ImpactNode = {
  id: string;
  codigo: string;
  tipo: string | null;
  distance?: number;
  severity?: string | null;
  path?: string[];
};

const severityClass: Record<string, string> = {
  CRITICO: 'fill-[var(--status-critico)]',
  ATENCAO: 'fill-[var(--status-atencao)]',
  NORMAL: 'fill-[var(--status-normal)]',
};

export function ImpactDiagram({ source, affected }: { source: ImpactNode; affected: ImpactNode[] }) {
  const nodes = [source, ...affected];
  const width = Math.max(560, nodes.length * 190);
  const height = 190;
  const nodeX = (index: number) => 30 + index * 180;

  return <div className="overflow-x-auto rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-3">
    <svg role="img" aria-labelledby="impact-diagram-title impact-diagram-desc" viewBox={`0 0 ${width} ${height}`} className="min-w-[560px] w-full">
      <title id="impact-diagram-title">Diagrama de impacto operacional</title>
      <desc id="impact-diagram-desc">{source.codigo} e as máquinas alcançáveis por vínculos cadastrados. A severidade só aparece quando veio associada ao nó.</desc>
      <defs><marker id="impact-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" className="fill-[var(--text-3)]" /></marker></defs>
      {affected.map((node, index) => <g key={`edge-${node.id}`}>
        <line x1={nodeX(0) + 130} y1="88" x2={nodeX(index + 1)} y2="88" stroke="currentColor" strokeWidth="1.5" markerEnd="url(#impact-arrow)" className="text-[var(--text-3)]" />
        <text x={(nodeX(0) + 130 + nodeX(index + 1)) / 2} y="72" textAnchor="middle" className="fill-[var(--text-3)] text-[9px]">{node.path?.join(' · ') || 'vínculo cadastrado'}</text>
      </g>)}
      {nodes.map((node, index) => <g key={node.id}>
        <rect x={nodeX(index)} y="55" width="130" height="66" rx="14" className={`${severityClass[node.severity ?? ''] ?? 'fill-[var(--panel-glass-strong)]'} stroke-[var(--line)]`} />
        <text x={nodeX(index) + 65} y="80" textAnchor="middle" className="fill-[var(--text-1)] text-[12px] font-semibold">{node.codigo}</text>
        <text x={nodeX(index) + 65} y="98" textAnchor="middle" className="fill-[var(--text-2)] text-[10px]">{node.tipo || 'tipo não informado'}</text>
        <text x={nodeX(index) + 65} y="113" textAnchor="middle" className="fill-[var(--text-3)] text-[9px]">{index === 0 ? 'origem' : `distância ${node.distance ?? '?'}`}</text>
      </g>)}
    </svg>
    <p className="mt-2 text-xs text-[var(--text-3)]">A seta mostra o alcance calculado pelos vínculos. Cor de severidade só é aplicada quando existe evento associado ao nó.</p>
  </div>;
}

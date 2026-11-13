'use client';

import type { SaudeMaquina } from '@/schemas/saude';
import { describeTrustFactor } from '@/lib/trustFactors';

export function TrustBadge({ health, compact = false }: { health: SaudeMaquina | null; compact?: boolean }) {
  if (!health || health.trust_score_medio === null) {
    return <span className="inline-flex rounded-full border border-[var(--line)] px-2.5 py-1 text-xs text-[var(--text-3)]">Confiança dos dados indisponível</span>;
  }
  const score = health.trust_score_medio;
  if (!Number.isFinite(score) || score < 0 || score > 1) {
    return <span role="status" className="inline-flex rounded-full border border-[var(--line)] px-2.5 py-1 text-xs text-[var(--text-2)]">Confiança dos dados inválida</span>;
  }
  const percent = Math.round(score * 100);
  const factors = health.fatores_ultima_leitura;
  return (
    <details className="group relative inline-block">
      <summary aria-label={`Dados ${percent}% confiáveis. Abrir explicação.`} className="min-h-8 cursor-pointer list-none rounded-full border border-[var(--line)] bg-[var(--panel-glass-mid)] px-3 py-1.5 text-xs font-semibold text-[var(--text-1)] outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--ui-accent)] [&::-webkit-details-marker]:hidden">
        Dados {percent}% confiáveis <span className="font-mono text-[var(--text-3)]">({Math.round(score * 100)}/100)</span>
      </summary>
      <div className={`z-30 mt-2 w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-[var(--line)] bg-[var(--panel)] p-3 text-left shadow-lg ${compact ? 'absolute right-0' : 'absolute left-0'}`}>
        <p className="text-xs font-semibold text-[var(--text-1)]">Trust Score agregado · escala 0–100</p>
        <p className="mt-1 text-[10px] leading-relaxed text-[var(--text-3)]">A pontuação é uma média móvel. Os itens abaixo são condições registradas na leitura mais recente; não são uma decomposição matemática da média.</p>
        {factors.length ? (
          <ul className="mt-3 space-y-2">
            {factors.map((factor, index) => {
              const definition = describeTrustFactor(factor.codigo);
              return <li key={`${factor.codigo}-${index}`} className="border-t border-[var(--line)] pt-2">
                <p className="text-xs font-medium text-[var(--text-1)]">{definition.title}</p>
                <p className="mt-0.5 text-[10px] leading-relaxed text-[var(--text-2)]">{definition.description}</p>
                <p className="mt-1 text-[10px] text-[var(--text-3)]">{factor.detalhe}{factor.peso === null ? ' · contribuição individual não rastreada' : ` · contribuição ${factor.peso}`}</p>
              </li>;
            })}
          </ul>
        ) : <p className="mt-2 text-xs text-[var(--text-2)]">Nenhum fator explicativo registrado na leitura mais recente.</p>}
      </div>
    </details>
  );
}

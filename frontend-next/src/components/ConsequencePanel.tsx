'use client';

import { useEffect, useState } from 'react';
import { ImpactDiagram, type ImpactNode } from '@/components/ImpactDiagram';

export type ConsequenceAssessment = {
  event_id: string;
  rule_version: string;
  afetados: Array<{ machine_id: string; codigo: string; tipo: string | null; distance: number; path: string[] }>;
  risco_parada: string;
  horizonte_minutos: number | null;
  horizonte_tipo: string | null;
  premissas: string[];
  faltantes: string[];
  confianca: string;
  needs_verification: boolean;
};

type Props = { eventId: string; source: ImpactNode; recommendation: string };

export function ConsequencePanel({ eventId, source, recommendation }: Props) {
  const [assessment, setAssessment] = useState<ConsequenceAssessment | null>(null);
  const [error, setError] = useState('');
  const [open, setOpen] = useState(true);

  useEffect(() => {
    let active = true;
    setAssessment(null); setError('');
    fetch(`/api/events/${eventId}/consequence/`, { cache: 'no-store', headers: { Accept: 'application/json' } })
      .then(async (response) => { if (!response.ok) throw new Error('Não foi possível consultar a avaliação de consequência.'); return response.json() as Promise<ConsequenceAssessment>; })
      .then((data) => { if (active) setAssessment(data); })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : 'Avaliação indisponível.'); });
    return () => { active = false; };
  }, [eventId]);

  return <section data-testid="consequence-panel" className="mt-5 rounded-2xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-4" aria-label="Consequência operacional">
    <div className="flex items-start justify-between gap-3"><div><p className="section-heading">Consequência operacional</p><h3 className="mt-1 text-base font-semibold text-[var(--text-1)]">Como este evento pode repercutir na operação</h3></div><button type="button" className="min-h-10 rounded-xl border border-[var(--line)] px-3 text-xs font-bold" aria-expanded={open} onClick={() => setOpen((value) => !value)}>{open ? 'Recolher' : 'Expandir'}</button></div>
    <section className="mt-4 rounded-xl border border-[color:var(--status-atencao)]/40 bg-[color:var(--status-atencao)]/5 p-3" aria-label="O que não sabemos"><h4 className="text-xs font-bold uppercase tracking-wider text-[var(--text-2)]">O que não sabemos</h4>{!assessment && !error ? <p className="mt-2 text-sm text-[var(--text-3)]">Consultando a avaliação...</p> : error ? <p role="alert" className="mt-2 text-sm text-[var(--status-critico)]">{error}</p> : <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--text-2)]">{assessment?.faltantes.length ? assessment.faltantes.map((item) => <li key={item}>{item}</li>) : <li>Nenhuma limitação registrada para esta avaliação.</li>}</ul>}</section>
    {open && assessment && <div className="mt-4 space-y-4">
      <section aria-label="O que aconteceu"><h4 className="section-heading">O que aconteceu</h4><p className="mt-2 text-sm text-[var(--text-2)]">A avaliação foi iniciada pelo evento registrado na máquina <strong className="text-[var(--text-1)]">{source.codigo}</strong>. Risco de parada calculado: <strong className="text-[var(--text-1)]">{assessment.risco_parada}</strong>. Regra: {assessment.rule_version}.</p></section>
      <section aria-label="Quem é afetado"><h4 className="section-heading">Quem é afetado · {assessment.afetados.length}</h4>{assessment.afetados.length ? <ul className="mt-2 space-y-2 text-sm text-[var(--text-2)]">{assessment.afetados.map((item) => <li key={item.machine_id}><strong className="text-[var(--text-1)]">{item.codigo}</strong> · {item.tipo || 'tipo não informado'} · distância {item.distance} · {item.path.join(' → ')}</li>)}</ul> : <p className="mt-2 text-sm text-[var(--text-3)]">Nenhuma máquina afetada foi identificada por vínculo válido.</p>}<div className="mt-3"><ImpactDiagram source={source} affected={assessment.afetados.map((item) => ({ id: item.machine_id, codigo: item.codigo, tipo: item.tipo, distance: item.distance, path: item.path }))} /></div></section>
      <section aria-label="Ação recomendada"><h4 className="section-heading">Ação recomendada</h4><p className="mt-2 text-sm text-[var(--text-2)]">{recommendation || 'Não há ação recomendada disponível para esta avaliação.'}</p>{assessment.premissas.length > 0 && <p className="mt-2 text-xs text-[var(--text-3)]">Premissas: {assessment.premissas.join(' · ')}</p>}</section>
    </div>}
  </section>;
}

import type { Telemetry } from '@/types/telemetry';

type DataHealth = NonNullable<Telemetry['data_health']>;
type TrustTone = 'trusted' | 'unstable' | 'suspect' | 'unknown';

const toneClasses: Record<TrustTone, string> = {
  trusted: 'border-status-normal/25 bg-status-normal/10 text-status-normal',
  unstable: 'border-status-atencao/25 bg-status-atencao/10 text-status-atencao',
  suspect: 'border-status-critico/25 bg-status-critico/10 text-status-critico',
  unknown: 'border-field-border bg-field-glass text-field-text3',
};

function trustTone(score?: number | null): TrustTone {
  if (score == null) return 'unknown';
  if (score >= 0.8) return 'trusted';
  if (score >= 0.6) return 'unstable';
  return 'suspect';
}

function trustLabel(tone: TrustTone) {
  if (tone === 'trusted') return 'Dado confiavel';
  if (tone === 'unstable') return 'Dado instavel';
  if (tone === 'suspect') return 'Sensor suspeito';
  return 'Sem health';
}

function tooltipText(dataHealth?: DataHealth | null) {
  if (!dataHealth || dataHealth.trust_score_medio == null) {
    return 'Data Health ainda sem leituras pontuadas para esta machine.';
  }

  const score = Math.round(dataHealth.trust_score_medio * 100);
  const motivos = dataHealth.sinais_de_alerta.ultimos_motivos || [];
  if (motivos.length === 0) {
    return `Trust Score medio ${score}%. Sem motivos recentes de alerta.`;
  }

  return `Trust Score medio ${score}%. Motivos: ${motivos.join('; ')}.`;
}

export function DataHealthBadge({ dataHealth }: { dataHealth?: DataHealth | null }) {
  const tone = trustTone(dataHealth?.trust_score_medio);
  const score =
    dataHealth?.trust_score_medio == null
      ? null
      : Math.round(dataHealth.trust_score_medio * 100);

  return (
    <span
      title={tooltipText(dataHealth)}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] ${toneClasses[tone]}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      <span>{trustLabel(tone)}</span>
      {score != null && <span className="font-mono">{score}%</span>}
    </span>
  );
}

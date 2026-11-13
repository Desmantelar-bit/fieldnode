import contract from '../../../contracts/attention.v1.json';

export type PriorityBand = 'P1' | 'P2' | 'P3';

export function classifyAttention(score: number | null, severity: string): PriorityBand | null {
  if (severity === 'CRITICO') return 'P1';
  if (score === null || !Number.isFinite(score) || score < 0 || score > 1) return null;
  if (score >= contract.classification.P1.min_score) return 'P1';
  if (score >= contract.classification.P2.min_score) return 'P2';
  return 'P3';
}

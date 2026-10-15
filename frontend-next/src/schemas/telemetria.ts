import { z } from 'zod';

function normalizeRiskLabel(value: string): string {
  const normalized = value
    .trim()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toUpperCase();

  if (normalized === 'CRITICO') return 'CRITICO';
  if (normalized === 'ALERTA' || normalized === 'ATENCAO') return 'ATENCAO';
  if (normalized === 'NORMAL') return 'NORMAL';
  return value.trim();
}

export const StatusRiscoSchema = z.preprocess(
  (val) => {
    if (typeof val === 'string' && val.trim()) {
      return { rotuloRisco: normalizeRiskLabel(val) };
    }
    if (val && typeof val === 'object' && !Array.isArray(val)) {
      const record = val as Record<string, unknown>;
      if (typeof record.rotuloRisco === 'string' && record.rotuloRisco.trim()) {
        return { ...record, rotuloRisco: normalizeRiskLabel(record.rotuloRisco) };
      }
    }
    return val;
  },
  z.object({
    nivelCor: z.string().optional(),
    nivelBg: z.string().optional(),
    rotuloRisco: z.string().optional(),
  }),
);

export const LeituraTelemetriaInputSchema = z.object({
  id: z.string().uuid().optional(),
  maquina_id: z.string().min(1),
  temperatura: z.coerce.number(),
  vibracao: z.coerce.number(),
  rpm: z.coerce.number().int(),
  latitude: z.coerce.number().min(-90).max(90).optional(),
  longitude: z.coerce.number().min(-180).max(180).optional(),
  timestamp: z.string().min(1),
});

export const LeituraTelemetriaSchema = z.preprocess(
  (val: unknown) => {
    if (val && typeof val === 'object') {
      const record = val as Record<string, unknown>;
      if (!record.status_risco && typeof record.nivel_risco === 'string' && record.nivel_risco.trim()) {
        return {
          ...record,
          status_risco: { rotuloRisco: record.nivel_risco.trim() },
        };
      }
    }
    return val;
  },
  LeituraTelemetriaInputSchema.extend({
    id: z.string().optional(),
    status_risco: StatusRiscoSchema.optional(),
    nivel_risco: z.string().optional(),
    total_leituras: z.coerce.number().optional(),
    recebido_em: z.string().optional(),
  }),
);

export const ListaLeiturasTelemetriaSchema = z.array(LeituraTelemetriaSchema);

export type LeituraTelemetria = z.infer<typeof LeituraTelemetriaSchema>;
export type LeituraTelemetriaInput = z.infer<typeof LeituraTelemetriaInputSchema>;

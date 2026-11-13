import { z } from 'zod';

const eventTypes = ['TEMP_ALTA', 'VIBRACAO_ALTA', 'ANOMALIA_ML', 'ANOMALIA_ESTATISTICA', 'TENDENCIA_RISCO'] as const;
const eventSeverity = ['NORMAL', 'ATENCAO', 'CRITICO'] as const;

export const EventoSchema = z.object({
  id: z.string().uuid(),
  machine: z.string().uuid(),
  machine_id: z.string().uuid(),
  machine_external_code: z.string(),
  leitura_origem: z.string().uuid().nullable(),
  leitura_origem_id: z.string().uuid().nullable(),
  tipo: z.enum(eventTypes),
  severidade: z.enum(eventSeverity),
  status: z.enum(['ABERTO', 'FECHADO']),
  trust_score_herdado: z.number().nullable(),
  evidence_quality: z.enum(['boa', 'suspeita', 'insuficiente']),
  needs_verification: z.boolean(),
  priority_score: z.string().regex(/^(?:0(?:\.\d{1,4})?|1(?:\.0{1,4})?)$/).transform(Number).nullable(),
  criado_em: z.string().datetime({ offset: true }),
  dados_contexto: z.record(z.unknown()),
});

export const EventoPageSchema = z.object({
  count: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  page_size: z.number().int().positive(),
  pages: z.number().int().nonnegative(),
  next: z.string().url().nullable(),
  previous: z.string().url().nullable(),
  results: z.array(EventoSchema),
});
export type Evento = z.infer<typeof EventoSchema>;
export type EventoPage = z.infer<typeof EventoPageSchema>;

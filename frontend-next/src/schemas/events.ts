import { z } from 'zod';

export const EventSchema = z.object({
  id: z.string().uuid(),
  machine_id: z.string().uuid(),
  machine_external_code: z.string(),
  tipo: z.string(),
  severidade: z.enum(['NORMAL', 'ATENCAO', 'CRITICO']),
  status: z.string(),
  trust_score_herdado: z.number().nullable(),
  priority_score: z.coerce.number().nullable(),
  evidence_quality: z.enum(['boa', 'suspeita', 'insuficiente']),
  needs_verification: z.boolean(),
  criado_em: z.string(),
});

export const EventListSchema = z.object({
  count: z.number().int().nonnegative(),
  results: z.array(EventSchema),
});

export type OperationalEvent = z.infer<typeof EventSchema>;

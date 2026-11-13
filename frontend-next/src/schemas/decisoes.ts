import { z } from 'zod';

export const DecisaoSchema = z.object({
  id: z.string().uuid(),
  machine: z.string().uuid(),
  machine_external_code: z.string(),
  event: z.string().uuid().nullable(),
  texto: z.string(),
  acao_recomendada: z.string(),
  severidade: z.enum(['NORMAL', 'ATENCAO', 'CRITICO']),
  confianca: z.number().min(0).max(1).nullable(),
  status: z.enum(['PENDENTE', 'APROVADA', 'REJEITADA', 'EXECUTADA', 'EXPIRADA']),
  criado_em: z.string().datetime({ offset: true }),
  decidido_por: z.number().int().nullable(),
  decidido_por_username: z.string().nullable().optional(),
  decidido_em: z.string().datetime({ offset: true }).nullable(),
  outcome_texto: z.string().nullable(),
  metodologia: z.string().nullable(),
});

export const DecisaoPageSchema = z.object({
  count: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  page_size: z.number().int().positive(),
  pages: z.number().int().nonnegative(),
  next: z.string().url().nullable(),
  previous: z.string().url().nullable(),
  results: z.array(DecisaoSchema),
});
export type Decisao = z.infer<typeof DecisaoSchema>;
export type DecisaoPage = z.infer<typeof DecisaoPageSchema>;

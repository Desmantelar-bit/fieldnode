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
  transicoes_permitidas: z.array(z.enum(['PENDENTE', 'APROVADA', 'REJEITADA', 'EXECUTADA', 'EXPIRADA'])).default([]),
  evidencia: z.object({
    evento: z.object({ id: z.string(), tipo: z.string(), severidade: z.string(), criado_em: z.string(), evidence_quality: z.string(), needs_verification: z.boolean(), dados_contexto: z.record(z.string(), z.unknown()) }),
    leitura: z.object({ id: z.string(), event_time: z.string().nullable(), time_source: z.string(), event_time_confidence: z.number(), temperatura: z.number(), vibracao: z.number(), rpm: z.number(), trust_score: z.number().nullable() }).nullable(),
  }).nullable().optional(),
  historico: z.array(z.object({ action: z.string(), quando: z.string(), ator: z.string().nullable(), metadata: z.record(z.string(), z.unknown()) })).optional(),
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

import { z } from 'zod';

export const DecisionStatusSchema = z.enum([
  'PENDENTE',
  'APROVADA',
  'REJEITADA',
  'EXECUTADA',
  'EXPIRADA',
]);

export const PrescricaoSchema = z.object({
  id: z.coerce.number().optional(),
  maquina_id: z.string().min(1),
  titulo: z.string().min(1),
  descricao: z.string(),
  status: z.enum(['pendente', 'concluida', 'cancelada']),
  data_geracao: z.string().min(1),
});

export const ListaPrescricoesSchema = z.array(PrescricaoSchema);

export type Prescricao = z.infer<typeof PrescricaoSchema>;

export const AnalisePrescricaoSchema = z.object({
  maquina_id: z.string().min(1),
  status: z.enum(['NORMAL', 'ATENCAO', 'CRITICO']),
  motivos: z.array(z.string()),
  metricas: z.record(z.string(), z.unknown()),
  recomendacao: z.string().nullable(),
  recomendacao_tecnica: z.string().nullable(),
  explicacao_operador: z.string().nullable(),
  fonte_explicacao: z.enum([
    'ia_generativa',
    'fallback_determinístico',
    'determinístico',
  ]),
  decision_id: z.string().uuid().optional(),
  decision_status: DecisionStatusSchema.optional(),
  gerado_em: z.string().min(1),
});

export type AnalisePrescricao = z.infer<typeof AnalisePrescricaoSchema>;

export const DecisionSchema = z.object({
  id: z.string().uuid(),
  status: DecisionStatusSchema,
  decidido_por: z.number().int().nullable(),
  decidido_por_username: z.string().nullable().optional(),
  decidido_em: z.string().nullable(),
  outcome_texto: z.string().nullable(),
});

export type Decision = z.infer<typeof DecisionSchema>;

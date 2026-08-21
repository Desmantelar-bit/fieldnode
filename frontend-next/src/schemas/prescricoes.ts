import { z } from 'zod';

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
  gerado_em: z.string().min(1),
});

export type AnalisePrescricao = z.infer<typeof AnalisePrescricaoSchema>;

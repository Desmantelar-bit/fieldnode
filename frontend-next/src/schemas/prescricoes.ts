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

import { z } from 'zod';

export const RelatorioResumoSchema = z.object({
  status: z.string().optional(),
  detalhe: z.string().optional(),
  periodo: z.string(),
  total_leituras: z.coerce.number(),
  maquinas_ativas: z.coerce.number(),
  alertas_gerados: z.coerce.number(),
  eficiencia_operacional: z.coerce.number(),
  dados: z.array(z.unknown()).optional(),
});

export type RelatorioResumo = z.infer<typeof RelatorioResumoSchema>;

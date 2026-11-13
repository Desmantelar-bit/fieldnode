import { z } from 'zod';

export const SaudeMaquinaSchema = z.object({
  machine_id: z.string().uuid(),
  external_code: z.string(),
  status: z.enum(['ok', 'sem_dados']),
  trust_score_medio: z.number().nullable(),
  ultima_atualizacao: z.string().datetime({ offset: true }).nullable(),
  leituras_analisadas: z.number().int().nonnegative(),
  sinais_de_alerta: z.record(z.unknown()),
  fatores_ultima_leitura: z.array(z.object({
    codigo: z.string(),
    peso: z.number().nullable(),
    detalhe: z.string(),
  })).default([]),
});
export type SaudeMaquina = z.infer<typeof SaudeMaquinaSchema>;

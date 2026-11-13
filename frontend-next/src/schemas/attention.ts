import { z } from 'zod';
import { EventoSchema } from '@/schemas/eventos';

export const AttentionSummarySchema = z.object({
  decisoes_pendentes: z.number().int().nonnegative(),
  riscos_criticos: z.number().int().nonnegative(),
  eventos_criticos: z.number().int().nonnegative(),
  maquinas_dados_instaveis: z.number().int().nonnegative(),
  eventos: z.array(EventoSchema),
});

export type AttentionSummary = z.infer<typeof AttentionSummarySchema>;

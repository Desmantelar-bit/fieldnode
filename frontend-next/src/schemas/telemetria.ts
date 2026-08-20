import { z } from 'zod';

export const StatusRiscoSchema = z.object({
  nivelCor: z.string().optional(),
  nivelBg: z.string().optional(),
  rotuloRisco: z.string().optional(),
});

export const LeituraTelemetriaInputSchema = z.object({
  id: z.string().uuid().optional(),
  maquina_id: z.string().min(1),
  temperatura: z.coerce.number(),
  vibracao: z.coerce.number(),
  rpm: z.coerce.number().int(),
  latitude: z.coerce.number().min(-90).max(90).optional(),
  longitude: z.coerce.number().min(-180).max(180).optional(),
  timestamp: z.string().min(1),
});

export const LeituraTelemetriaSchema = LeituraTelemetriaInputSchema.extend({
  id: z.string().optional(),
  status_risco: StatusRiscoSchema.optional(),
  nivel_risco: z.string().optional(),
  total_leituras: z.coerce.number().optional(),
  recebido_em: z.string().optional(),
});

export const ListaLeiturasTelemetriaSchema = z.array(LeituraTelemetriaSchema);

export type LeituraTelemetria = z.infer<typeof LeituraTelemetriaSchema>;
export type LeituraTelemetriaInput = z.infer<typeof LeituraTelemetriaInputSchema>;

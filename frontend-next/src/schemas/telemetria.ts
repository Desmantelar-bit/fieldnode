import { z } from 'zod';

export const StatusRiscoSchema = z.object({
  nivelCor: z.string().optional(),
  nivelBg: z.string().optional(),
  rotuloRisco: z.string().optional(),
});

export const DataHealthSchema = z.object({
  machine_id: z.string(),
  external_code: z.string().nullable().optional(),
  status: z.enum(['ok', 'sem_dados']).default('sem_dados'),
  trust_score_medio: z.coerce.number().min(0).max(1).nullable(),
  ultima_atualizacao: z.string().nullable(),
  leituras_analisadas: z.coerce.number().default(0),
  sinais_de_alerta: z
    .object({
      primeira_leitura: z.boolean().optional(),
      gap_temporal: z.boolean().optional(),
      timestamp_fora_de_ordem: z.boolean().optional(),
      timestamp_indisponivel: z.boolean().optional(),
      valores_repetidos: z.boolean().optional(),
      limite_fisico: z.boolean().optional(),
      salto_abrupto: z.boolean().optional(),
      score_baixo: z.boolean().optional(),
      contadores: z.record(z.coerce.number()).optional(),
      ultimos_motivos: z.array(z.string()).optional(),
    })
    .catchall(z.unknown())
    .default({}),
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
  data_health: DataHealthSchema.nullable().optional(),
});

export const ListaLeiturasTelemetriaSchema = z.array(LeituraTelemetriaSchema);

export type LeituraTelemetria = z.infer<typeof LeituraTelemetriaSchema>;
export type LeituraTelemetriaInput = z.infer<typeof LeituraTelemetriaInputSchema>;

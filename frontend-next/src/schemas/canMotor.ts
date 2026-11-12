import { z } from 'zod';

const CanReadingSchema = z.object({
  id: z.string().uuid(),
  maquina_id: z.string(),
  timestamp: z.string(),
  recebido_em: z.string(),
  simulado: z.boolean(),
  rpm: z.number().nullable(),
  carga_pct: z.number().nullable(),
  horimetro_h: z.number().nullable(),
  oleo_pressao_kpa: z.number().nullable(),
  oleo_temp_c: z.number().nullable(),
  oleo_nivel_pct: z.number().nullable(),
  liquido_temp_c: z.number().nullable(),
  liquido_nivel_pct: z.number().nullable(),
  rail_pressao_kpa: z.number().nullable(),
  combustivel_temp_c: z.number().nullable(),
  consumo_lh: z.number().nullable(),
  turbo_pressao_kpa: z.number().nullable(),
  escape_temp_c: z.number().nullable(),
  bateria_v: z.number().nullable(),
});

export const CanMotorSchema = z.object({
  ultima_leitura: CanReadingSchema.nullable(),
  serie: z.array(CanReadingSchema),
  dtcs_ativos: z.array(z.object({
    spn: z.number().int(),
    fmi: z.number().int().min(0).max(31),
    ocorrencias: z.number().int().nonnegative(),
    ativo: z.boolean(),
    primeira_vez: z.string(),
    ultima_vez: z.string(),
    subsistema: z.string(),
    descricao_referencia: z.string().nullable(),
    simulado: z.boolean(),
  })),
  prescricoes: z.array(z.object({
    subsistema: z.string(),
    status: z.enum(['NORMAL', 'ATENCAO', 'CRITICO']).nullable(),
    evidencia_nivel: z.enum(['BAIXA', 'MEDIA', 'ALTA']),
    sinais_usados: z.array(z.object({
      sinal: z.string(),
      valor: z.number(),
      unidade: z.string(),
      concorda: z.boolean(),
    })),
    sinais_indisponiveis: z.array(z.string()),
    horas_ate_limite: z.number().nullable(),
    limite_referencia: z.object({
      sinal: z.string(),
      valor: z.number(),
      unidade: z.string(),
      direcao: z.enum(['acima', 'abaixo']),
      origem: z.string(),
    }).nullable(),
    motivo_estimativa: z.string(),
    diagnostico: z.string(),
    acao: z.string(),
    prazo: z.string(),
    dtcs_relacionados: z.array(z.object({
      spn: z.number().int(),
      fmi: z.number().int(),
      descricao_referencia: z.string(),
    })),
  })),
  qualidade: z.object({
    recebidas: z.number().int().nonnegative(),
    aceitas: z.number().int().nonnegative(),
    descartadas: z.number().int().nonnegative(),
    motivos: z.record(z.string(), z.number().int().nonnegative()),
    campos_ausentes: z.record(z.string(), z.number().int().nonnegative()),
    sinais_congelados: z.record(z.string(), z.number().int().nonnegative()),
  }),
  simulado: z.boolean(),
  origem_dados: z.enum(['SIMULADO', 'REAL', 'MISTO']),
});

export type CanReading = z.infer<typeof CanReadingSchema>;
export type CanMotorResponse = z.infer<typeof CanMotorSchema>;

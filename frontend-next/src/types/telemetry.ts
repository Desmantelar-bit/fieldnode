import { z } from 'zod';

const NamedRefSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { nome: 'Nao informado' };
  },
  z.object({
    nome: z.string().default('Nao informado'),
  })
);

const MachineModelSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { nome: 'Modelo nao informado', marca: { nome: 'Marca nao informada' } };
  },
  z.object({
    nome: z.string().default('Modelo nao informado'),
    marca: NamedRefSchema.default({ nome: 'Marca nao informada' }),
  })
);

const OperationStatusSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { em_operacao: false, tempo_de_operacao: 0 };
  },
  z.object({
    em_operacao: z.boolean().default(false),
    tempo_de_operacao: z.coerce.number().default(0),
  })
);

const MovementStatusSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { em_movimento: false, velocidade: 0 };
  },
  z.object({
    em_movimento: z.boolean().default(false),
    velocidade: z.coerce.number().default(0),
  })
);

export const TelemetryInputSchema = z.object({
  id: z.string().uuid().optional(),
  maquina_id: z.string().min(1),
  temperatura: z.coerce.number(),
  vibracao: z.coerce.number(),
  rpm: z.coerce.number().int(),
  timestamp: z.string().min(1),
});

export const TelemetrySchema = TelemetryInputSchema.extend({
  nivel_risco: z.enum(['NORMAL', 'ATENCAO', 'CRITICO']).optional(),
  total_leituras: z.coerce.number().optional(),
});

export const MachineFleetSchema = z.object({
  id: z.coerce.number(),
  modelo: MachineModelSchema,
  operario: NamedRefSchema.default({ nome: 'Sem operador' }),
  status_de_operacao: OperationStatusSchema,
  estado_de_movimento: MovementStatusSchema,
});

export type Telemetry = z.infer<typeof TelemetrySchema>;
export type TelemetryInput = z.infer<typeof TelemetryInputSchema>;
export type Machine = z.infer<typeof MachineFleetSchema>;

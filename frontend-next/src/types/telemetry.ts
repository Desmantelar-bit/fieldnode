import { z } from 'zod';

export const TelemetrySchema = z.object({
  id: z.string().uuid(),
  maquina_id: z.string(),
  temperatura: z.number(),
  vibracao: z.number(),
  rpm: z.number().int(),
  timestamp: z.string().datetime(),
});

export const MachineFleetSchema = z.object({
  id: z.number(),
  modelo: z.object({
    nome: z.string(),
    marca: z.object({ nome: z.string() }),
  }),
  operario: z.object({ nome: z.string() }),
  status_de_operacao: z.object({
    em_operacao: z.boolean(),
    tempo_de_operacao: z.number(),
  }),
  estado_de_movimento: z.object({
    em_movimento: z.boolean(),
    velocidade: z.number(),
  }),
});

export type Telemetry = z.infer<typeof TelemetrySchema>;
export type Machine = z.infer<typeof MachineFleetSchema>;
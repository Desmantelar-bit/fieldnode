import { z } from 'zod';
import {
  ColheitadeiraSchema,
  ListaColheitadeirasSchema,
  ListaPosicoesMaquinasSchema,
  PosicaoMaquinaSchema,
  AnalisePrescricaoSchema,
  PrescricaoSchema,
  RelatorioResumoSchema,
  TelemetryInputSchema,
  TelemetrySchema,
} from '@/schemas';

export {
  ColheitadeiraSchema as MachineFleetSchema,
  ListaColheitadeirasSchema,
  ListaPosicoesMaquinasSchema,
  PosicaoMaquinaSchema as MachinePositionSchema,
  PrescricaoSchema,
  RelatorioResumoSchema as RelatorioSchema,
  TelemetryInputSchema,
  TelemetrySchema,
};

export const OperatorSchema = z.object({
  id: z.coerce.number(),
  nome: z.string().default('Operario sem nome'),
  tempo_de_servico: z.coerce.number().default(0),
  no_banco: z.boolean().default(false),
});

export type Telemetry = z.infer<typeof TelemetrySchema>;
export type TelemetryInput = z.infer<typeof TelemetryInputSchema>;
export type Machine = z.infer<typeof ColheitadeiraSchema>;
export type MachinePosition = z.infer<typeof PosicaoMaquinaSchema>;
export type Operator = z.infer<typeof OperatorSchema>;
export type Prescricao = z.infer<typeof PrescricaoSchema>;
export type AnalisePrescricao = z.infer<typeof AnalisePrescricaoSchema>;
export type Relatorio = z.infer<typeof RelatorioResumoSchema>;

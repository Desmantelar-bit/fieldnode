import { z } from 'zod';

const NamedRefSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { nome: 'Nao informado' };
  },
  z.object({
    nome: z.string().default('Nao informado'),
  }),
);

const MachineModelSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { nome: 'Modelo nao informado', marca: { nome: 'Marca nao informada' } };
  },
  z.object({
    nome: z.string().default('Modelo nao informado'),
    marca: NamedRefSchema.default({ nome: 'Marca nao informada' }),
  }),
);

const OperationStatusSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { em_operacao: false, tempo_de_operacao: 0 };
  },
  z.object({
    em_operacao: z.boolean().default(false),
    tempo_de_operacao: z.coerce.number().default(0),
  }),
);

const MovementStatusSchema = z.preprocess(
  (value) => {
    if (value && typeof value === 'object') return value;
    return { em_movimento: false, velocidade: 0 };
  },
  z.object({
    em_movimento: z.boolean().default(false),
    velocidade: z.coerce.number().default(0),
  }),
);

export const ColheitadeiraSchema = z.object({
  id: z.coerce.number(),
  ativo: z.boolean().optional(),
  maquina_id: z.string().optional(),
  modelo: MachineModelSchema,
  operario: NamedRefSchema.default({ nome: 'Sem operador' }),
  status_de_operacao: OperationStatusSchema,
  estado_de_movimento: MovementStatusSchema,
});

export const ListaColheitadeirasSchema = z.array(ColheitadeiraSchema);

export const PosicaoMaquinaSchema = z.object({
  id: z.coerce.number(),
  maquina_id: z.string().optional(),
  modelo: z.string(),
  lat: z.coerce.number(),
  lng: z.coerce.number(),
  status: z.string(),
  telemetria: z.object({
    temperatura: z.coerce.number(),
    rpm: z.coerce.number(),
    timestamp: z.string(),
  }),
});

export const ListaPosicoesMaquinasSchema = z.array(PosicaoMaquinaSchema);

export type Colheitadeira = z.infer<typeof ColheitadeiraSchema>;
export type PosicaoMaquina = z.infer<typeof PosicaoMaquinaSchema>;

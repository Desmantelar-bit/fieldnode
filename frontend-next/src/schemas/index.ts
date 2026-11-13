export {
  LeituraTelemetriaInputSchema as TelemetryInputSchema,
  LeituraTelemetriaSchema as TelemetrySchema,
  ListaLeiturasTelemetriaSchema,
  StatusRiscoSchema,
  type LeituraTelemetria,
  type LeituraTelemetriaInput,
} from './telemetria';
export {
  ColheitadeiraSchema,
  ListaColheitadeirasSchema,
  ListaPosicoesMaquinasSchema,
  PosicaoMaquinaSchema,
  type Colheitadeira,
  type PosicaoMaquina,
} from './maquinas';
export {
  AnalisePrescricaoSchema,
  ListaPrescricoesSchema,
  PrescricaoSchema,
  type AnalisePrescricao,
  type Prescricao,
} from './prescricoes';
export {
  RelatorioResumoSchema,
  type RelatorioResumo,
} from './relatorios';
export { EventoSchema, EventoPageSchema, type Evento, type EventoPage } from './eventos';
export { DecisaoSchema, DecisaoPageSchema, type Decisao, type DecisaoPage } from './decisoes';
export { SaudeMaquinaSchema, type SaudeMaquina } from './saude';

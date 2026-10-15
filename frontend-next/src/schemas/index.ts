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

import {
  MachineFleetSchema,
  OperatorSchema,
  TelemetryInputSchema,
  TelemetrySchema,
  PrescricaoSchema,
  RelatorioSchema,
  type Machine,
  type Operator,
  type Telemetry,
  type TelemetryInput,
  type Prescricao,
  type Relatorio,
} from '@/types/telemetry';

declare const process: { env: Record<string, string | undefined> };

const API_URL =
  typeof window === 'undefined'
    ? (process.env.FIELDNODE_SERVER_API_URL || 'http://web:8000/api')
    : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api');
const API_KEY = process.env.NEXT_PUBLIC_FIELDNODE_API_KEY || '';
const API_TIMEOUT_MS = 10000;

function withTimeout<T>(promise: Promise<T>): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  return promise.finally(() => clearTimeout(timer));
}

export const telemetryService = {
  async getFleetStatus(): Promise<Machine[]> {
    const headers = new Headers({ Accept: 'application/json' });
    if (API_KEY) headers.set('X-API-Key', API_KEY);
    const response = await withTimeout(fetch(`${API_URL}/colheitadeira/`, { cache: 'no-store', headers }));
    if (!response.ok) throw new Error('Falha ao buscar frota');
    const data = await response.json();
    return MachineFleetSchema.array().parse(data);
  },

  async getLatestReadings(): Promise<Telemetry[]> {
    const response = await withTimeout(fetch(`${API_URL}/leituras/ultimas/`, {
      headers: new Headers({ Accept: 'application/json' }),
    }));
    if (!response.ok) throw new Error('Falha ao buscar telemetria');
    const data = await response.json();
    return TelemetrySchema.array().parse(data);
  },

  async getMachineReadings(machineId: string): Promise<Telemetry[]> {
    const response = await withTimeout(fetch(`${API_URL}/telemetria/?maquina_id=${encodeURIComponent(machineId)}`, {
      cache: 'no-store',
      headers: new Headers({ Accept: 'application/json' }),
    }));
    if (!response.ok) throw new Error('Falha ao buscar historico da maquina');
    const data = await response.json();
    return TelemetrySchema.array().parse(data);
  },

  async getOperators(): Promise<Operator[]> {
    const headers = new Headers({ Accept: 'application/json' });
    if (API_KEY) headers.set('X-API-Key', API_KEY);
    const response = await withTimeout(fetch(`${API_URL}/operario/`, { cache: 'no-store', headers }));
    if (!response.ok) throw new Error('Falha ao buscar operarios');
    const data = await response.json();
    return OperatorSchema.array().parse(data);
  },

  async sendTelemetry(reading: TelemetryInput) {
    const payload = TelemetryInputSchema.parse(reading);
    const headers = new Headers({
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
    });
    const response = await withTimeout(fetch(`${API_URL}/telemetria/`, { method: 'POST', headers, body: JSON.stringify(payload) }));
    if (!response.ok) throw new Error(`Falha ao enviar telemetria: ${response.status}`);
    return response.json();
  },

  async queueTelemetry(reading: TelemetryInput) {
    if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) {
      return telemetryService.sendTelemetry(reading);
    }

    const registration = await navigator.serviceWorker.ready;
    const worker = registration.active || navigator.serviceWorker.controller;
    worker?.postMessage({
      type: 'QUEUE_TELEMETRY',
      payload: reading,
      headers: API_KEY ? { 'X-API-Key': API_KEY } : {},
    });

    return { status: 'queued' };
  },

  async getPrescricao(machineId: string): Promise<Prescricao> {
    const headers = new Headers({ Accept: 'application/json' });
    if (API_KEY) headers.set('X-API-Key', API_KEY);
    const response = await withTimeout(fetch(`${API_URL}/prescricoes/?maquina_id=${encodeURIComponent(machineId)}`, { cache: 'no-store', headers }));
    if (!response.ok) throw new Error(`Falha ao buscar prescrição: ${response.status}`);
    const data = await response.json();
    
    if (!Array.isArray(data) || data.length === 0) {
      throw new Error('API retornou dados inválidos ou vazios');
    }
    
    return PrescricaoSchema.parse(data[0]);
  },

  async getRelatorio(formato?: 'json' | 'csv'): Promise<Relatorio> {
    const headers = new Headers({ Accept: 'application/json' });
    if (API_KEY) headers.set('X-API-Key', API_KEY);
    const url = formato ? `${API_URL}/relatorio/?formato=${formato}` : `${API_URL}/relatorio/?formato=json`;
    const response = await withTimeout(fetch(url, { cache: 'no-store', headers }));
    if (!response.ok) throw new Error(`Falha ao buscar relatório: ${response.status}`);
    const data = await response.json();
    
    return RelatorioSchema.parse(data);
  },
};

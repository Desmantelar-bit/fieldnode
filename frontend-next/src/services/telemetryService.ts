import {
  MachineFleetSchema,
  OperatorSchema,
  TelemetryInputSchema,
  TelemetrySchema,
  type Machine,
  type Operator,
  type Telemetry,
  type TelemetryInput,
} from '@/types/telemetry';

const API_URL =
  process.env.FIELDNODE_SERVER_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://127.0.0.1:8000/api';
const API_KEY = process.env.NEXT_PUBLIC_FIELDNODE_API_KEY || '';
const API_TIMEOUT_MS = 5000;

function apiSignal() {
  return AbortSignal.timeout(API_TIMEOUT_MS);
}

export const telemetryService = {
  async getFleetStatus(): Promise<Machine[]> {
    const response = await fetch(`${API_URL}/colheitadeira/`, {
      cache: 'no-store',
      signal: apiSignal(),
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) throw new Error('Falha ao buscar frota');
    const data = await response.json();
    return parseMachineFleet(data);
  },

  async getLatestReadings(): Promise<Telemetry[]> {
    const response = await fetch(`${API_URL}/leituras/ultimas/`, {
      next: { revalidate: 10 },
      signal: apiSignal(),
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) throw new Error('Falha ao buscar telemetria');
    const data = await response.json();
    return parseTelemetryList(data);
  },

  async getMachineReadings(machineId: string): Promise<Telemetry[]> {
    const response = await fetch(`${API_URL}/telemetria/?maquina_id=${encodeURIComponent(machineId)}`, {
      cache: 'no-store',
      signal: apiSignal(),
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) throw new Error('Falha ao buscar historico da maquina');
    const data = await response.json();
    return parseTelemetryList(data);
  },

  async getOperators(): Promise<Operator[]> {
    const response = await fetch(`${API_URL}/operario/`, {
      cache: 'no-store',
      signal: apiSignal(),
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) throw new Error('Falha ao buscar operarios');
    const data = await response.json();
    return OperatorSchema.array().parse(data);
  },

  async sendTelemetry(reading: TelemetryInput) {
    const payload = TelemetryInputSchema.parse(reading);
    const response = await fetch(`${API_URL}/telemetria/`, {
      method: 'POST',
      signal: apiSignal(),
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok && response.status !== 202) {
      throw new Error('Falha ao enviar telemetria');
    }

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
};

function parseMachineFleet(data: unknown): Machine[] {
  return MachineFleetSchema.array().parse(data);
}

function parseTelemetryList(data: unknown): Telemetry[] {
  return TelemetrySchema.array().parse(data);
}

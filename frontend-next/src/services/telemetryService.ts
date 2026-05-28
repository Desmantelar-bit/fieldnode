import { z } from 'zod';
import { MachineFleetSchema, TelemetrySchema } from '@/types/telemetry';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

export const telemetryService = {
  async getFleetStatus() {
    const response = await fetch(`${API_URL}/colheitadeira/`, {
      cache: 'no-store',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error('Falha ao buscar frota');
    const data = await response.json();
    return z.array(MachineFleetSchema).parse(data);
  },

  async getLatestReadings() {
    const response = await fetch(`${API_URL}/leituras/ultimas/`, {
      next: { revalidate: 10 },
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error('Falha ao buscar telemetria');
    const data = await response.json();
    return z.array(TelemetrySchema).parse(data);
  }
};
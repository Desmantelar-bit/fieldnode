import { SaudeMaquinaSchema, type SaudeMaquina } from '@/schemas/saude';
import { getValidated } from '@/services/apiRead';

export const healthService = {
  get(machineId: string, signal?: AbortSignal): Promise<SaudeMaquina> {
    return getValidated(`machines/${encodeURIComponent(machineId)}/health/`, SaudeMaquinaSchema, signal);
  },
};

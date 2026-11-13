import { DecisaoPageSchema, type DecisaoPage } from '@/schemas/decisoes';
import { getValidated } from '@/services/apiRead';

export type DecisionFilters = { maquina_id?: string; status?: string; severidade?: string; page?: number; page_size?: number };
export const decisionService = {
  list(filters: DecisionFilters = {}, signal?: AbortSignal): Promise<DecisaoPage> {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(filters)) if (value !== undefined) query.set(key, String(value));
    const suffix = query.size ? `?${query.toString()}` : '';
    return getValidated(`decisions/${suffix}`, DecisaoPageSchema, signal);
  },
};

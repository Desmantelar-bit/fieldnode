import { EventoPageSchema, type EventoPage } from '@/schemas/eventos';
import { getValidated } from '@/services/apiRead';

export type EventFilters = { maquina_id?: string; tipo?: string; severidade?: string; status?: string; page?: number; page_size?: number };
export const eventService = {
  list(filters: EventFilters = {}, signal?: AbortSignal): Promise<EventoPage> {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(filters)) if (value !== undefined) query.set(key, String(value));
    const suffix = query.size ? `?${query.toString()}` : '';
    return getValidated(`events/${suffix}`, EventoPageSchema, signal);
  },
};

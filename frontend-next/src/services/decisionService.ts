import { DecisaoPageSchema, DecisaoSchema, type Decisao, type DecisaoPage } from '@/schemas/decisoes';
import { getValidated } from '@/services/apiRead';
import { enqueueAction } from '@/lib/offline/actions';

export class OfflineActionQueuedError extends Error {
  queued = true;
  constructor() { super('Sem conexão. A ação foi guardada e será reaplicada quando o gateway voltar.'); }
}

export type DecisionFilters = { maquina_id?: string; status?: string; severidade?: string; page?: number; page_size?: number };
export const decisionService = {
  list(filters: DecisionFilters = {}, signal?: AbortSignal): Promise<DecisaoPage> {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(filters)) if (value !== undefined) query.set(key, String(value));
    const suffix = query.size ? `?${query.toString()}` : '';
    return getValidated(`decisions/${suffix}`, DecisaoPageSchema, signal);
  },
  async update(id: string, status: string, outcome_texto?: string, motivo_rejeicao?: string): Promise<Decisao> {
    const body = { status, ...(outcome_texto !== undefined ? { outcome_texto } : {}), ...(motivo_rejeicao !== undefined ? { motivo_rejeicao } : {}) };
    const key = crypto.randomUUID();
    let response: Response;
    try {
      response = await fetch(`/api/decisions/${id}/`, {
        method: 'PATCH',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-FieldNode-CSRF': '1', 'Idempotency-Key': key },
        credentials: 'include', body: JSON.stringify(body),
      });
    } catch {
      await enqueueAction({ type: status === 'APROVADA' ? 'decision.approve' : 'decision.reject', id, body, key });
      throw new OfflineActionQueuedError();
    }
    if (response.status === 202) {
      await enqueueAction({ type: status === 'APROVADA' ? 'decision.approve' : 'decision.reject', id, body, key });
      throw new OfflineActionQueuedError();
    }
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try { const body = await response.json(); detail = body.detalhe || JSON.stringify(body); } catch { /* response is not JSON */ }
      throw new Error(detail);
    }
    return DecisaoSchema.parse(await response.json());
  },
};

import type { z } from 'zod';

export type ApiFailureKind = 'auth' | 'forbidden' | 'not_found' | 'rate_limit' | 'server' | 'network' | 'timeout' | 'http' | 'invalido';

export class ApiReadError extends Error {
  constructor(public readonly kind: ApiFailureKind, message: string, public readonly status?: number) {
    super(message);
    this.name = 'ApiReadError';
  }
}

export async function getValidated<T extends z.ZodType>(path: string, schema: T, signal?: AbortSignal): Promise<z.infer<T>> {
  const controller = new AbortController();
  let timedOut = false;
  const abort = () => controller.abort(signal?.reason);
  if (signal?.aborted) abort();
  else signal?.addEventListener('abort', abort, { once: true });
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, 10_000);
  try {
    const response = await fetch(`/api/${path.replace(/^\/+/, '')}`, {
      method: 'GET',
      credentials: 'same-origin',
      cache: 'no-store',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });
    if (!response.ok) {
      const kind: ApiFailureKind = response.status === 401 ? 'auth'
        : response.status === 403 ? 'forbidden'
        : response.status === 404 ? 'not_found'
        : response.status === 429 ? 'rate_limit'
        : response.status >= 500 ? 'server' : 'http';
      throw new ApiReadError(kind, `A API respondeu com HTTP ${response.status}.`, response.status);
    }

    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new ApiReadError('invalido', 'A API retornou uma resposta que não é JSON.', response.status);
    }
    const parsed = schema.safeParse(payload);
    if (!parsed.success) {
      if (process.env.NODE_ENV !== 'production') {
        console.error('Contrato de leitura incompatível', { path, issues: parsed.error.issues });
      }
      throw new ApiReadError('invalido', 'Os dados recebidos não correspondem ao contrato esperado.', response.status);
    }
    return parsed.data;
  } catch (error) {
    if (signal?.aborted || error instanceof ApiReadError) throw error;
    throw new ApiReadError(timedOut ? 'timeout' : 'network', timedOut ? 'Tempo limite da API excedido.' : 'Não foi possível conectar à API.');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
}

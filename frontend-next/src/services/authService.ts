export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthResult { user: AuthUser }
export interface AuthError { field?: 'username' | 'email' | 'password' | 'general'; message: string }

const USER_KEY = 'fn-auth-user';

export function isAuthAvailable(): boolean { return true; }

export function getUser(): AuthUser | null {
  if (typeof window === 'undefined') return null;
  try {
    const value = localStorage.getItem(USER_KEY);
    return value ? JSON.parse(value) as AuthUser : null;
  } catch { return null; }
}

function storeUser(user: AuthUser) {
  try {
    localStorage.removeItem('fn-auth-token');
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch { /* storage can be disabled */ }
}

export function clearSession() {
  try {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem('fn-auth-token');
  } catch { /* storage can be disabled */ }
}

async function clearPrivateOfflineCache(): Promise<void> {
  const deletions: Promise<boolean>[] = [];
  if (typeof window !== 'undefined' && 'caches' in window) {
    deletions.push(
      caches.keys().then(async (cacheNames) => {
        const privateCaches = cacheNames.filter((name) => name.startsWith('fieldnode-runtime-'));
        await Promise.all(privateCaches.map((name) => caches.delete(name)));
        return privateCaches.length > 0;
      }),
    );
  }
  if (typeof navigator !== 'undefined') {
    navigator.serviceWorker?.controller?.postMessage({ type: 'CLEAR_PRIVATE_CACHE' });
  }
  await Promise.all(deletions);
}

async function parseError(response: Response): Promise<AuthError> {
  const body = await response.json().catch(() => ({})) as Record<string, unknown>;

  if (Array.isArray(body.non_field_errors) && body.non_field_errors.length > 0) {
    return { field: 'general', message: String(body.non_field_errors[0]) };
  }

  const errors = (body.errors && typeof body.errors === 'object' ? body.errors : body) as Record<string, unknown>;
  for (const field of ['username', 'password', 'email'] as const) {
    const val = errors[field];
    if (val) {
      const msg = Array.isArray(val) ? val[0] : val;
      return { field, message: String(msg) };
    }
  }

  const fallback = body.error || body.detail || (typeof body.message === 'string' ? body.message : undefined);
  if (fallback) {
    return { field: 'general', message: String(fallback) };
  }

  return { field: 'general', message: `Erro inesperado (HTTP ${response.status}).` };
}

async function submit(path: string, payload: unknown): Promise<AuthResult> {
  let response: Response;
  try {
    response = await fetch(`/api/auth/${path}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(payload),
      cache: 'no-store',
    });
  } catch {
    throw { field: 'general', message: 'Serviço de autenticação indisponível. Verifique a conexão com o servidor.' } satisfies AuthError;
  }
  if (!response.ok) throw await parseError(response);
  const body = await response.json() as { user?: AuthUser };
  if (!body.user || typeof body.user.username !== 'string') {
    throw { field: 'general', message: 'Resposta de autenticação inválida.' } satisfies AuthError;
  }
  storeUser(body.user);
  return { user: body.user };
}

export function login(username: string, password: string): Promise<AuthResult> {
  return submit('login', { username, password });
}

export function register(params: {
  username: string; email: string; password: string; first_name?: string; last_name?: string;
}): Promise<AuthResult> {
  return submit('register', params);
}

export async function logout(): Promise<void> {
  try {
    await fetch('/api/auth/logout/', { method: 'POST', credentials: 'same-origin', cache: 'no-store' });
  } finally {
    clearSession();
    await clearPrivateOfflineCache();
  }
}

export async function verifyToken(): Promise<AuthUser | null> {
  try {
    const response = await fetch('/api/auth/me/', { credentials: 'same-origin', cache: 'no-store' });
    if (response.status === 401 || response.status === 403) {
      clearSession();
      await clearPrivateOfflineCache();
      return null;
    }
    if (!response.ok) throw new Error(`Falha ao verificar sessão (HTTP ${response.status}).`);
    const user = await response.json() as AuthUser;
    storeUser(user);
    return user;
  } catch { throw new Error('Não foi possível verificar a sessão.'); }
}

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

async function parseError(response: Response): Promise<AuthError> {
  const body = await response.json().catch(() => ({})) as Record<string, unknown>;
  const errors = body.errors as Record<string, unknown> | undefined;
  const key = errors && Object.keys(errors)[0];
  if (key) return { field: key as AuthError['field'], message: String(errors[key]) };
  return { field: 'general', message: String(body.error || body.detail || `Erro inesperado (HTTP ${response.status}).`) };
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
  } finally { clearSession(); }
}

export async function verifyToken(): Promise<AuthUser | null> {
  try {
    const response = await fetch('/api/auth/me/', { credentials: 'same-origin', cache: 'no-store' });
    if (response.status === 401 || response.status === 403) { clearSession(); return null; }
    if (!response.ok) throw new Error(`Falha ao verificar sessão (HTTP ${response.status}).`);
    const user = await response.json() as AuthUser;
    storeUser(user);
    return user;
  } catch { throw new Error('Não foi possível verificar a sessão.'); }
}

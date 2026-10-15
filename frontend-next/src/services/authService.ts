/**
 * authService.ts — Serviço de autenticação do FieldNode.
 *
 * Gerencia login, registro, logout e persistência do token DRF.
 * O token é armazenado em localStorage com a chave "fn-auth-token".
 * O objeto user é armazenado como JSON em "fn-auth-user".
 *
 * Nenhum dado sensível é exposto além do necessário para a sessão.
 */

declare const process: { env: Record<string, string | undefined> };

/**
 * Base das rotas de autenticação (/api/auth/*).
 *
 * No navegador, o padrão é falar com a MESMA ORIGEM: o `next.config.ts` já
 * reescreve `/api/*` para o Django, então a requisição não sai do domínio da
 * aplicação e não esbarra em CORS — funciona em qualquer porta de dev, sem
 * precisar liberar origem no backend.
 *
 * `NEXT_PUBLIC_API_URL` continua tendo prioridade quando definida. Ela é aceita
 * tanto na forma raiz (`http://host:8000`) quanto já terminando em `/api`, para
 * nunca montar `/api/api/...` por engano.
 */
function resolveAuthBase(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();

  if (!configured) {
    // Mesma origem: o rewrite do Next encaminha para o backend.
    if (typeof window === "undefined") {
      return process.env.FIELDNODE_SERVER_API_URL?.trim() || "http://127.0.0.1:8000/api";
    }
    return "/api";
  }

  const trimmed = configured.replace(/\/+$/, "");
  if (trimmed === "/api" || trimmed.endsWith("/api") || trimmed.includes("/api/")) {
    return trimmed;
  }
  return `${trimmed}/api`;
}

const AUTH_BASE = resolveAuthBase();

/** Monta a URL de um endpoint de autenticação sobre a base resolvida. */
function authUrl(path: string): string {
  return `${AUTH_BASE}${path}`;
}

/**
 * A autenticação está alcançável? Sim sempre que existir uma base — o caminho
 * de mesma origem vale em dev e em produção (o rewrite é incondicional). O que
 * pode falhar é a requisição em si, e isso vira erro de formulário honesto.
 */
export function isAuthAvailable(): boolean {
  return Boolean(AUTH_BASE);
}

const TOKEN_KEY = "fn-auth-token";
const USER_KEY  = "fn-auth-user";

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthResult {
  token: string;
  user: AuthUser;
}

export interface AuthError {
  /** Campo de formulário afetado (undefined = erro geral) */
  field?: "username" | "email" | "password" | "general";
  message: string;
}

// ── Armazenamento ──────────────────────────────────────────────────────────

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}

function persistSession(result: AuthResult): void {
  localStorage.setItem(TOKEN_KEY, result.token);
  localStorage.setItem(USER_KEY, JSON.stringify(result.user));
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// ── Headers ────────────────────────────────────────────────────────────────

export function authHeaders(): HeadersInit {
  const token = getToken();
  if (!token) return { "Content-Type": "application/json" };
  return {
    "Content-Type": "application/json",
    Authorization: `Token ${token}`,
  };
}

// ── Helpers internos ───────────────────────────────────────────────────────

function backendUnavailable(): AuthError {
  return {
    field: "general",
    message:
      "Serviço de autenticação indisponível. Verifique a conexão com o servidor.",
  };
}

async function parseError(res: Response): Promise<AuthError> {
  try {
    const json = await res.json();

    // { "errors": { "username": "..." } } — erros por campo
    if (json.errors && typeof json.errors === "object") {
      const fields = Object.keys(json.errors);
      const first  = fields[0];
      if (first) {
        return {
          field: first as AuthError["field"],
          message: (json.errors as Record<string, string>)[first] ?? "Erro desconhecido.",
        };
      }
    }

    // { "error": "..." } — erro geral
    if (json.error) return { field: "general", message: json.error };

    // { "detail": "..." } — padrão DRF
    if (json.detail) return { field: "general", message: json.detail };
  } catch {
    // corpo não é JSON
  }

  return { field: "general", message: `Erro inesperado (HTTP ${res.status}).` };
}

// ── API ────────────────────────────────────────────────────────────────────

/**
 * Executa requisição com suporte a caminhos alternativos se o endpoint padrão retornar 404.
 */
async function fetchWithFallback(
  primaryPath: string,
  fallbackPaths: string[],
  init: RequestInit
): Promise<Response> {
  const res = await fetch(authUrl(primaryPath), init);
  if (res.status === 404 && fallbackPaths.length > 0) {
    for (const alt of fallbackPaths) {
      try {
        const altRes = await fetch(authUrl(alt), init);
        if (altRes.status !== 404) {
          return altRes;
        }
      } catch {
        // prossegue para o próximo caminho alternativo
      }
    }
  }
  return res;
}

/**
 * Autentica o usuário.
 * Lança AuthError em caso de falha; retorna AuthResult em caso de sucesso.
 * Suporta resposta com `{ token, user }` ou resposta padrão DRF `{ token }` / `{ key }`.
 */
export async function login(
  username: string,
  password: string
): Promise<AuthResult> {
  let res: Response;
  try {
    res = await fetchWithFallback("/auth/login/", ["/login/", "/api-token-auth/"], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw backendUnavailable();
  }

  if (!res.ok) throw await parseError(res);

  const rawData = (await res.json()) as Record<string, unknown>;
  const token =
    (typeof rawData.token === "string" && rawData.token) ||
    (typeof rawData.key === "string" && rawData.key) ||
    (typeof rawData.access === "string" && rawData.access) ||
    "";

  if (!token) {
    throw {
      field: "general",
      message: "O servidor respondeu com sucesso, mas não forneceu um token de acesso válido.",
    };
  }

  const userObj = rawData.user && typeof rawData.user === "object" ? (rawData.user as Record<string, unknown>) : null;
  const user: AuthUser = {
    id: typeof userObj?.id === "number" ? userObj.id : (typeof rawData.id === "number" ? rawData.id : 0),
    username: typeof userObj?.username === "string" ? userObj.username : username,
    email: typeof userObj?.email === "string" ? userObj.email : (typeof rawData.email === "string" ? rawData.email : ""),
    first_name: typeof userObj?.first_name === "string" ? userObj.first_name : (typeof rawData.first_name === "string" ? rawData.first_name : username),
    last_name: typeof userObj?.last_name === "string" ? userObj.last_name : (typeof rawData.last_name === "string" ? rawData.last_name : ""),
  };

  const result: AuthResult = { token, user };
  persistSession(result);
  return result;
}

/**
 * Registra um novo usuário.
 * Lança AuthError em caso de falha; retorna AuthResult em caso de sucesso.
 */
export async function register(params: {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}): Promise<AuthResult> {
  let res: Response;
  try {
    res = await fetchWithFallback("/auth/register/", ["/register/"], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
  } catch {
    throw backendUnavailable();
  }

  if (!res.ok) throw await parseError(res);

  const rawData = (await res.json()) as Record<string, unknown>;
  const token =
    (typeof rawData.token === "string" && rawData.token) ||
    (typeof rawData.key === "string" && rawData.key) ||
    (typeof rawData.access === "string" && rawData.access) ||
    "";

  if (!token) {
    throw {
      field: "general",
      message: "O servidor respondeu com sucesso, mas não forneceu um token de acesso válido.",
    };
  }

  const userObj = rawData.user && typeof rawData.user === "object" ? (rawData.user as Record<string, unknown>) : null;
  const user: AuthUser = {
    id: typeof userObj?.id === "number" ? userObj.id : (typeof rawData.id === "number" ? rawData.id : 0),
    username: typeof userObj?.username === "string" ? userObj.username : params.username,
    email: typeof userObj?.email === "string" ? userObj.email : params.email,
    first_name: typeof userObj?.first_name === "string" ? userObj.first_name : (params.first_name || params.username),
    last_name: typeof userObj?.last_name === "string" ? userObj.last_name : (params.last_name || ""),
  };

  const result: AuthResult = { token, user };
  persistSession(result);
  return result;
}

/**
 * Invalida o token no backend e limpa a sessão local.
 */
export async function logout(): Promise<void> {
  const token = getToken();
  clearSession();

  if (!token) return;

  try {
    await fetchWithFallback("/auth/logout/", ["/logout/"], {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
    });
  } catch {
    // falha silenciosa — sessão local já foi limpa
  }
}

/**
 * Verifica se o token ainda é válido no backend.
 * Limpa a sessão local se inválido.
 */
export async function verifyToken(): Promise<AuthUser | null> {
  const token = getToken();
  if (!token) return null;

  try {
    const res = await fetchWithFallback("/auth/me/", ["/me/", "/user/"], {
      headers: { Authorization: `Token ${token}` },
    });

    if (res.ok) {
      const user = (await res.json()) as AuthUser;
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      return user;
    }

    // Token inválido/expirado
    clearSession();
    return null;
  } catch {
    return null;
  }
}

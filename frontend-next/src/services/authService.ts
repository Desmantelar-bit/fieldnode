/**
 * authService.ts — Serviço de autenticação do FieldNode.
 *
 * Gerencia login, encerramento local de sessão e persistência do token DRF.
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
export const AUTH_EXPIRED_EVENT = "fieldnode:auth-expired";

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

export function handleUnauthorizedResponse(response: { status: number }): void {
  if (response.status !== 401 || typeof window === "undefined") return;
  clearSession();
  window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
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

    if (Array.isArray(json.non_field_errors) && json.non_field_errors.length) {
      return { field: "general", message: String(json.non_field_errors[0]) };
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
 * Autentica o usuário.
 * Lança AuthError em caso de falha; retorna AuthResult em caso de sucesso.
 * Consome o contrato implementado: `{ token, expires_in, user_id, username }`.
 */
export async function login(
  username: string,
  password: string
): Promise<AuthResult> {
  let res: Response;
  try {
    res = await fetch(authUrl("/auth/login/"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw backendUnavailable();
  }

  if (!res.ok) throw await parseError(res);

  const rawData = (await res.json()) as Record<string, unknown>;
  const token = typeof rawData.token === "string" ? rawData.token : "";
  const userId = rawData.user_id;
  const authenticatedUsername = rawData.username;

  if (
    !token ||
    typeof userId !== "number" ||
    typeof authenticatedUsername !== "string" ||
    !authenticatedUsername
  ) {
    throw {
      field: "general",
      message: "O servidor respondeu com dados de autenticação incompletos.",
    };
  }

  const user: AuthUser = {
    id: userId,
    username: authenticatedUsername,
    email: typeof rawData.email === "string" ? rawData.email : "",
    first_name: typeof rawData.first_name === "string" ? rawData.first_name : "",
    last_name: typeof rawData.last_name === "string" ? rawData.last_name : "",
  };

  const result: AuthResult = { token, user };
  persistSession(result);
  return result;
}

/**
 * O backend não implementa cadastro público; rejeita sem enviar credenciais.
 */
export async function register(_params: {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}): Promise<AuthResult> {
  void _params;
  throw {
    field: "general",
    message: "O cadastro de usuários ainda não está disponível nesta API.",
  } satisfies AuthError;
}

/**
 * O backend atual não expõe revogação de token; encerra a sessão local.
 */
export async function logout(): Promise<void> {
  clearSession();
}

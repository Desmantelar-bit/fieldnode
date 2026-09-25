"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Eye,
  EyeOff,
  LoaderCircle,
  LockKeyhole,
  RadioTower,
  ShieldCheck,
  Tractor,
  UserRound,
} from "lucide-react";
import {
  AUTH_TOKEN_STORAGE_KEY,
  resolveApiUrl,
} from "@/services/telemetryService";

type LoginResponse = {
  token?: unknown;
};

function extractErrorMessage(status: number, body: string): string {
  if (status === 400 || status === 401) {
    return "Usuario ou senha invalidos.";
  }

  if (body.trim()) {
    return `Falha no login: ${body}`;
  }

  return "Nao foi possivel autenticar agora. Confira a API e tente novamente.";
}

function hasTokenPayload(data: unknown): data is { token: string } {
  return (
    typeof data === "object" &&
    data !== null &&
    "token" in data &&
    typeof (data as LoginResponse).token === "string" &&
    (data as { token: string }).token.trim().length > 0
  );
}

export default function LoginPage() {
  const router = useRouter();
  const usernameId = "fieldnode-login-username";
  const passwordId = "fieldnode-login-password";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const apiUrl = useMemo(() => resolveApiUrl(), []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const trimmedUsername = username.trim();
    if (!trimmedUsername || !password) {
      setError("Preencha usuario e senha para entrar.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch(`${apiUrl}/auth/login/`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: trimmedUsername,
          password,
        }),
      });

      if (!response.ok) {
        const body = await response.text().catch(() => "");
        throw new Error(extractErrorMessage(response.status, body));
      }

      const data: unknown = await response.json();
      if (!hasTokenPayload(data)) {
        throw new Error("A API autenticou, mas nao retornou um token valido.");
      }

      window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, data.token);
      document.cookie = `fieldnode_token=${data.token}; path=/; SameSite=Lax`;
      const requestedNext = new URLSearchParams(window.location.search).get("next");
      const next = requestedNext?.startsWith("/") && !requestedNext.startsWith("//")
        ? requestedNext
        : "/dashboard";
      router.replace(next);
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Erro inesperado ao autenticar.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-[image:var(--surface-page)] text-field-text">
      <section className="mx-auto grid min-h-screen w-full max-w-6xl grid-cols-1 px-4 py-6 sm:px-6 lg:grid-cols-[1fr_420px] lg:items-center lg:gap-12 lg:px-8">
        <div className="hidden lg:block">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 border border-status-normal/20 bg-status-normal/10 px-3 py-2 text-xs font-semibold uppercase tracking-label text-status-normal">
              <RadioTower className="h-4 w-4" aria-hidden="true" />
              Console administrativo
            </div>

            <h1 className="mt-8 max-w-lg text-4xl font-semibold tracking-title text-field-text1">
              FieldNode
            </h1>
            <p className="mt-4 max-w-md text-sm leading-6 text-field-text3">
              Acesso autenticado para registrar dados e operar o painel de
              telemetria agricola sem abrir a porteira para qualquer request
              perdida.
            </p>

            <div className="mt-10 grid max-w-lg grid-cols-3 gap-3">
              {[
                { label: "API", value: "DRF Token" },
                { label: "Destino", value: "/dashboard" },
                { label: "Storage", value: "MVP/TCC" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="border border-field-border bg-field-glass p-4"
                >
                  <p className="text-[11px] font-semibold uppercase tracking-label text-field-text3">
                    {item.label}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-field-text1">
                    {item.value}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-6 border-l border-status-normal/40 pl-4 text-sm leading-6 text-field-text3">
              O token gravado aqui alimenta automaticamente as chamadas do
              frontend que usam o servico de telemetria.
            </div>
          </div>
        </div>

        <div className="flex min-h-[calc(100vh-3rem)] items-center justify-center lg:min-h-0">
          <form
            className="glass-panel w-full max-w-[420px] rounded-[var(--radius-panel)] p-5 sm:p-6"
            onSubmit={handleSubmit}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="inline-flex h-11 w-11 items-center justify-center border border-status-normal/25 bg-status-normal/10 text-status-normal">
                  <Tractor className="h-5 w-5" aria-hidden="true" />
                </div>
                <p className="mt-5 text-[11px] font-semibold uppercase tracking-label text-accent">
                  FieldNode
                </p>
                <h2 className="mt-2 text-2xl font-semibold tracking-title text-field-text1">
                  Entrar no painel
                </h2>
              </div>

              <div className="hidden items-center gap-2 border border-field-border bg-field-glass px-3 py-2 text-xs font-semibold text-field-text3 sm:inline-flex">
                <ShieldCheck className="h-4 w-4 text-status-normal" />
                Token DRF
              </div>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <label
                  className="text-xs font-semibold uppercase tracking-label text-field-text3"
                  htmlFor={usernameId}
                >
                  Usuario
                </label>
                <div className="mt-2 flex items-center gap-3 border border-field-border bg-field-glass px-3 focus-within:border-status-normal/70 focus-within:ring-2 focus-within:ring-[var(--focus-ring)]">
                  <UserRound
                    className="h-4 w-4 shrink-0 text-field-text3"
                    aria-hidden="true"
                  />
                  <input
                    id={usernameId}
                    autoComplete="username"
                    className="min-h-12 w-full bg-transparent text-sm text-field-text1 outline-none placeholder:text-field-text3"
                    disabled={isSubmitting}
                    name="username"
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder="admin"
                    type="text"
                    value={username}
                  />
                </div>
              </div>

              <div>
                <label
                  className="text-xs font-semibold uppercase tracking-label text-field-text3"
                  htmlFor={passwordId}
                >
                  Senha
                </label>
                <div className="mt-2 flex items-center gap-3 border border-field-border bg-field-glass px-3 focus-within:border-status-normal/70 focus-within:ring-2 focus-within:ring-[var(--focus-ring)]">
                  <LockKeyhole
                    className="h-4 w-4 shrink-0 text-field-text3"
                    aria-hidden="true"
                  />
                  <input
                    id={passwordId}
                    autoComplete="current-password"
                    className="min-h-12 w-full bg-transparent text-sm text-field-text1 outline-none placeholder:text-field-text3"
                    disabled={isSubmitting}
                    name="password"
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="sua senha"
                    type={showPassword ? "text" : "password"}
                    value={password}
                  />
                  <button
                    aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                    className="inline-flex h-11 w-11 shrink-0 items-center justify-center text-field-text3 transition hover:text-field-text1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-status-normal"
                    disabled={isSubmitting}
                    onClick={() => setShowPassword((current) => !current)}
                    type="button"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" aria-hidden="true" />
                    ) : (
                      <Eye className="h-4 w-4" aria-hidden="true" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error ? (
              <div
                className="mt-4 flex items-start gap-3 border border-status-critico/35 bg-status-critico/10 p-3 text-sm text-field-text2"
                role="alert"
              >
                <AlertTriangle
                  className="mt-0.5 h-4 w-4 shrink-0 text-status-critico"
                  aria-hidden="true"
                />
                <span>{error}</span>
              </div>
            ) : null}

            <button
              className="mt-6 inline-flex min-h-12 w-full items-center justify-center gap-2 bg-status-normal px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-lime-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-status-normal disabled:cursor-not-allowed disabled:opacity-60 active:scale-[0.99]"
              disabled={isSubmitting}
              type="submit"
            >
              {isSubmitting ? (
                <LoaderCircle
                  className="h-4 w-4 animate-spin"
                  aria-hidden="true"
                />
              ) : (
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              )}
              {isSubmitting ? "Autenticando" : "Entrar"}
            </button>

            <p className="mt-4 border border-field-border bg-field-glass p-3 text-xs leading-5 text-field-text3">
              Divida tecnica assumida: este MVP salva token em localStorage, o
              que e vulneravel a XSS. A evolucao correta e migrar para cookie
              httpOnly quando o fluxo de auth amadurecer.
            </p>
          </form>
        </div>
      </section>
    </main>
  );
}

"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, CheckCircle2, Eye, EyeOff, Loader2 } from "lucide-react";
import { AuthLayout } from "@/components/AuthLayout";
import { FieldNodeLogo } from "@/components/FieldNodeLogo";
import { register, verifyToken, isAuthAvailable, type AuthError } from "@/services/authService";

/* ──────────────────────────────────────────────────────────────────────────
   Cadastro — FieldNode
   Integrado ao endpoint POST /api/auth/register/ via authService.

   Mesma resolução de base do login: por padrão a chamada vai para a mesma
   origem, via o rewrite /api/* do next.config.ts. Sem aviso de variável de
   ambiente — a ausência dela é o caminho normal, não um defeito.
   ────────────────────────────────────────────────────────────────────────── */

const HAS_BACKEND = isAuthAvailable();

type FormState = "idle" | "loading" | "error" | "success";

export default function RegisterPage() {
  const router = useRouter();
  const fieldRef = useRef<HTMLInputElement>(null);

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [formState, setFormState] = useState<FormState>("idle");
  const [error, setError] = useState<AuthError | null>(null);

  /* redireciona se já autenticado */
  useEffect(() => {
    verifyToken().then((user) => { if (user) router.replace("/dashboard"); }).catch(() => {});
  }, [router]);

  /* foco automático */
  useEffect(() => {
    fieldRef.current?.focus();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (formState === "loading") return;

    setError(null);

    if (!username.trim()) {
      setError({ field: "username", message: "Escolha um nome de usuário." });
      return;
    }
    if (!password) {
      setError({ field: "password", message: "Defina uma senha." });
      return;
    }

    setFormState("loading");

    try {
      await register({
        username: username.trim(),
        email: email.trim(),
        password,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
      });
      setFormState("success");
      setTimeout(() => router.push("/dashboard"), 1200);
    } catch (err) {
      setFormState("error");
      setError(err as AuthError);
    }
  }

  const isLoading = formState === "loading";

  /* ── Tela de sucesso ── */
  if (formState === "success") {
    return (
      <AuthLayout>
        <div className="auth-card flex flex-col items-center gap-3 text-center" role="status">
          <CheckCircle2 size={48} className="text-[color:var(--status-normal)]" aria-hidden="true" />
          <h1 className="font-[family-name:var(--font-display)] text-xl font-bold text-[var(--text-1)]">
            Conta criada!
          </h1>
          <p className="text-sm text-[var(--text-3)]">Redirecionando para o dashboard…</p>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      headline={
        <>
          Comece a ler a <em>telemetria</em> da sua frota hoje.
        </>
      }
    >
      <div className="auth-card">
        {/* ── Cabeçalho do card ──
            Mesmo tratamento do login: sem selo de conexão, com o lockup
            horizontal e a assinatura da marca. */}
        <header className="flex flex-col items-center gap-3 text-center">
          <FieldNodeLogo variant="horizontal" className="mx-auto" />

          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[var(--text-1)]">
              Criar conta
            </h1>
            <p className="mt-1.5 text-[13px] text-[var(--text-3)]">
              Acesso restrito à equipe de operação
            </p>
          </div>
        </header>

        {/* ── Formulário ── */}
        <form onSubmit={handleSubmit} noValidate aria-label="Formulário de cadastro" className="mt-5 flex flex-col gap-4">
          {error?.field === "general" && (
            <div className="auth-error-block" role="alert">
              {error.message}
            </div>
          )}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="auth-field auth-field--pill">
              <label htmlFor="fn-first">Nome</label>
              <input
                ref={fieldRef}
                id="fn-first"
                type="text"
                autoComplete="given-name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                disabled={isLoading || !HAS_BACKEND}
                className="auth-input"
                placeholder="João"
              />
            </div>
            <div className="auth-field auth-field--pill">
              <label htmlFor="fn-last">Sobrenome</label>
              <input
                id="fn-last"
                type="text"
                autoComplete="family-name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                disabled={isLoading || !HAS_BACKEND}
                className="auth-input"
                placeholder="Silva"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <div className="auth-field auth-field--pill">
              <label htmlFor="fn-username">
                Nome de usuário <span className="text-[color:var(--status-critico)]">*</span>
              </label>
              <input
                id="fn-username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setError(null);
                }}
                disabled={isLoading || !HAS_BACKEND}
                aria-required="true"
                aria-describedby={error?.field === "username" ? "fn-username-err" : undefined}
                aria-invalid={error?.field === "username"}
                className="auth-input"
                placeholder="joao_silva"
              />
            </div>
            {error?.field === "username" && (
              <span id="fn-username-err" className="auth-field-error pl-4" role="alert">
                {error.message}
              </span>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <div className="auth-field auth-field--pill">
              <label htmlFor="fn-email">
                E-mail <span className="opacity-60">(opcional)</span>
              </label>
              <input
                id="fn-email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError(null);
                }}
                disabled={isLoading || !HAS_BACKEND}
                aria-describedby={error?.field === "email" ? "fn-email-err" : undefined}
                aria-invalid={error?.field === "email"}
                className="auth-input"
                placeholder="joao@empresa.com.br"
              />
            </div>
            {error?.field === "email" && (
              <span id="fn-email-err" className="auth-field-error pl-4" role="alert">
                {error.message}
              </span>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <div className="auth-field auth-field--pill">
              <label htmlFor="fn-password">
                Senha <span className="text-[color:var(--status-critico)]">*</span>
              </label>
              <div className="relative flex items-center">
                <input
                  id="fn-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError(null);
                  }}
                  disabled={isLoading || !HAS_BACKEND}
                  aria-required="true"
                  aria-describedby={
                    error?.field === "password" ? "fn-password-err" : "fn-password-hint"
                  }
                  aria-invalid={error?.field === "password"}
                  className="auth-input w-full pr-9"
                  placeholder="Mínimo 8 caracteres"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                  onClick={() => setShowPassword((v) => !v)}
                  disabled={isLoading}
                  className="absolute right-0 top-1/2 flex -translate-y-1/2 items-center justify-center rounded-md p-1 text-[var(--text-3)] transition-colors duration-150 hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
                >
                  {showPassword ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
                </button>
              </div>
            </div>
            {error?.field === "password" ? (
              <span id="fn-password-err" className="auth-field-error pl-4" role="alert">
                {error.message}
              </span>
            ) : (
              <span id="fn-password-hint" className="pl-4 text-[11px] text-[var(--text-3)]">
                Use letras, números e símbolos para uma senha mais segura.
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading || !HAS_BACKEND}
            aria-busy={isLoading}
            className="auth-submit mt-1"
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" aria-hidden="true" /> Criando conta…
              </>
            ) : (
              <>
                Criar conta <ArrowRight size={16} aria-hidden="true" />
              </>
            )}
          </button>
        </form>

        {/* ── Rodapé ── */}
        <footer className="mt-5 text-center text-[13px] text-[var(--text-3)]">
          Já tem conta?{" "}
          <Link href="/login" className="auth-link">
            Entrar
          </Link>
        </footer>
      </div>
    </AuthLayout>
  );
}

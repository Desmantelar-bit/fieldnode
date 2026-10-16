"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { FieldNodeLogo } from "@/components/FieldNodeLogo";
import { login, verifyToken, isAuthAvailable, type AuthError } from "@/services/authService";

/* ──────────────────────────────────────────────────────────────────────────
   Login — FieldNode
   Fundo: foto de campo verde (field-backdrop.jpg). Card: blur real, sem
   gradiente, sem glassmorphism com borda brilhante. Logo menor, centralizado.
   Sem título de produto — o formulário é o protagonista.
   ────────────────────────────────────────────────────────────────────────── */

const HAS_BACKEND = isAuthAvailable();

type FormState = "idle" | "loading" | "error" | "success";

export default function LoginPage() {
  const router = useRouter();
  const fieldRef = useRef<HTMLInputElement>(null);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [formState, setFormState] = useState<FormState>("idle");
  const [error, setError] = useState<AuthError | null>(null);

  useEffect(() => {
    verifyToken().then((user) => { if (user) router.replace("/dashboard"); }).catch(() => {});
  }, [router]);

  useEffect(() => {
    fieldRef.current?.focus();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (formState === "loading") return;
    setError(null);

    if (!username.trim()) {
      setError({ field: "username", message: "Informe seu nome de usuário." });
      return;
    }
    if (!password) {
      setError({ field: "password", message: "Informe sua senha." });
      return;
    }

    setFormState("loading");
    try {
      await login(username.trim(), password);
      setFormState("success");
      router.push("/dashboard");
    } catch (err) {
      setFormState("error");
      setError(err as AuthError);
    }
  }

  const isLoading = formState === "loading" || formState === "success";

  return (
    <div className="login-stage">
      {/* Fundo fotográfico — campo verde */}
      <div className="login-bg" aria-hidden="true" />
      {/* Véu levíssimo para o card destacar */}
      <div className="login-veil" aria-hidden="true" />

      <main className="login-center">
        <div className="login-card">
          {/* Logo compacto e centralizado */}
          <div className="flex justify-center mb-6">
            <FieldNodeLogo variant="stacked" />
          </div>

          {/* Título curto */}
          <h1 className="login-title">Bem-vindo de volta</h1>
          <p className="login-sub">Acesse sua conta para continuar</p>

          {/* Formulário */}
          <form onSubmit={handleSubmit} noValidate aria-label="Formulário de login" className="mt-7 flex flex-col gap-4">
            {error?.field === "general" && (
              <div className="auth-error-block" role="alert">
                {error.message}
              </div>
            )}

            {/* Usuário */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="fn-username" className="login-label">
                Usuário
              </label>
              <input
                ref={fieldRef}
                id="fn-username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => { setUsername(e.target.value); setError(null); }}
                disabled={isLoading || !HAS_BACKEND}
                aria-invalid={error?.field === "username"}
                aria-describedby={error?.field === "username" ? "fn-un-err" : undefined}
                className="login-input"
                placeholder="seu_usuario"
              />
              {error?.field === "username" && (
                <span id="fn-un-err" className="auth-field-error" role="alert">
                  {error.message}
                </span>
              )}
            </div>

            {/* Senha */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="fn-password" className="login-label">
                Senha
              </label>
              <div className="relative">
                <input
                  id="fn-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(null); }}
                  disabled={isLoading || !HAS_BACKEND}
                  aria-invalid={error?.field === "password"}
                  aria-describedby={error?.field === "password" ? "fn-pw-err" : undefined}
                  className="login-input w-full pr-11"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                  onClick={() => setShowPassword((v) => !v)}
                  disabled={isLoading}
                  className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center justify-center w-8 h-8 rounded-lg text-[rgba(255,255,255,0.5)] hover:text-white transition-colors duration-150 focus-visible:outline focus-visible:outline-2"
                >
                  {showPassword ? <EyeOff size={15} aria-hidden="true" /> : <Eye size={15} aria-hidden="true" />}
                </button>
              </div>
              {error?.field === "password" && (
                <span id="fn-pw-err" className="auth-field-error" role="alert">
                  {error.message}
                </span>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading || !HAS_BACKEND}
              aria-busy={formState === "loading"}
              className="login-btn mt-2"
            >
              {formState === "loading" ? (
                <><Loader2 size={16} className="animate-spin" aria-hidden="true" /> Entrando…</>
              ) : formState === "success" ? (
                <><Loader2 size={16} className="animate-spin" aria-hidden="true" /> Redirecionando…</>
              ) : (
                "Entrar"
              )}
            </button>
          </form>

          {/* Rodapé */}
          <p className="mt-6 text-center text-[13px] text-[rgba(255,255,255,0.52)]">
            Não tem conta?{" "}
            <Link href="/register" className="auth-link font-semibold">
              Criar conta
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}

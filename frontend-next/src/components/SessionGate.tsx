'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { AUTH_EXPIRED_EVENT, isAuthenticated } from '@/services/authService';

/* ──────────────────────────────────────────────────────────────────────────
   SessionGate — fecha a porta depois do logout.

   Fica dentro do AppShell, então cobre de uma vez todas as rotas do app
   (dashboard, mapa, colheitadeiras, operários, relatórios, máquinas, detalhes
   e prescrição), sem repetir a regra em cada página. `/login` e `/register`
   usam AuthLayout e ficam de fora, como deve ser.

   ── Sobre o que isto é e o que não é ──
   É uma guarda de EXPERIÊNCIA: sem sessão, o usuário é levado ao login em vez de
   ver um app que ele não deveria ver. NÃO é fronteira de segurança: o token
  mora em localStorage, então quem quiser entrar pode escrever a chave à mão.
  A proteção real é imposta pelas permissões do backend, que validam o token e
  o acesso às máquinas; a guarda visual não substitui essas permissões.
   ────────────────────────────────────────────────────────────────────────── */

export function SessionGate({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [denied, setDenied] = useState(false);

  useEffect(() => {
    if (isAuthenticated()) return;
    setDenied(true);
    router.replace('/login');
  }, [router]);

  useEffect(() => {
    function onSessionExpired() {
      setDenied(true);
      router.replace('/login');
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, onSessionExpired);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, onSessionExpired);
  }, [router]);

  // A guarda melhora a experiência, mas não substitui a autorização no backend.
  if (denied) {
    return <div className="app-background h-screen w-screen" aria-hidden="true" />;
  }

  return <>{children}</>;
}

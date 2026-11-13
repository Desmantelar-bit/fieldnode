'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { verifyToken } from '@/services/authService';

/* ──────────────────────────────────────────────────────────────────────────
   SessionGate — fecha a porta depois do logout.

   Fica dentro do AppShell, então cobre de uma vez todas as rotas do app
   (dashboard, mapa, colheitadeiras, operários, relatórios, máquinas, detalhes
   e prescrição), sem repetir a regra em cada página. `/login` e `/register`
   usam AuthLayout e ficam de fora, como deve ser.

   A sessão é validada pelo BFF. Se o servidor estiver indisponível, a falha de
   rede preserva a experiência offline; uma resposta 401/403 encerra a sessão.

   ── Sobre o que isto é e o que não é ──
   É uma guarda de experiência. A autorização dos dados continua no backend;
   este componente não substitui as permissões das APIs.
   ────────────────────────────────────────────────────────────────────────── */

export function SessionGate({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [denied, setDenied] = useState(false);

  useEffect(() => {
    let active = true;
    const check = () => verifyToken().then((user) => {
      if (!active || user) return;
      setDenied(true);
      router.replace('/login');
    }).catch(() => { /* Preserve offline access when the server cannot be reached. */ });
    check();
    const interval = window.setInterval(check, 60_000);
    window.addEventListener('focus', check);
    return () => {
      active = false;
      window.clearInterval(interval);
      window.removeEventListener('focus', check);
    };
  }, [router]);

  // Sem sessão: o conteúdo do app nunca é exibido. O SSR continua renderizando
  // as páginas normalmente (por isso o dashboard mantém as leituras iniciais no
  // HTML); esta troca só acontece no cliente, e só para quem não tem sessão.
  if (denied) {
    return <div className="app-background h-screen w-screen" aria-hidden="true" />;
  }

  return <>{children}</>;
}

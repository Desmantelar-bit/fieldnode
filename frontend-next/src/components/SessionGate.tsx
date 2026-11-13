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

   ── Sobre a "tolerância offline" ──
   A verificação é a PRESENÇA do token no storage, nunca uma ida ao servidor.
   Isso é o que faz a guarda conviver com o offline-first: com o token salvo, a
   guarda não faz requisição alguma e o app abre normalmente mesmo com o Django
   fora do ar. Trocar isso por um `verifyToken()` na entrada seria pior em dois
   sentidos — atrasaria toda navegação com uma chamada de rede e, quando o
   servidor estivesse fora, expulsaria um usuário que está legitimamente logado.

   ── Sobre o que isto é e o que não é ──
   É uma guarda de EXPERIÊNCIA: sem sessão, o usuário é levado ao login em vez de
   ver um app que ele não deveria ver. NÃO é fronteira de segurança: o token
   mora em localStorage, então quem quiser entrar pode escrever a chave à mão.
   Proteção de verdade só existe no servidor, e para isso o backend precisa
   negar os dados sem credencial — os endpoints de telemetria hoje são abertos.
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

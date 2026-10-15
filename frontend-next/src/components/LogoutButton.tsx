'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, LogOut } from 'lucide-react';
import { logout } from '@/services/authService';

/* ──────────────────────────────────────────────────────────────────────────
   LogoutButton — saída da sessão.

   Onde vive:
     · `rail`   — no pé do navigation rail (desktop), logo acima do indicador
                  de gateway. Reaproveita as classes `app-nav__item` e
                  `app-nav__tooltip` do Sidebar, então o botão tem exatamente o
                  mesmo hover, foco e tooltip dos itens de navegação.
     · `header` — variante para a barra do topo. HOJE NÃO É USADA: a saída no
                  mobile passou a viver no menu do `UserProfile`, que já mostra
                  os dados da sessão — dois botões de sair no mesmo cabeçalho
                  seriam redundantes. A variante fica disponível para telas
                  densas onde um ícone seja preferível a um menu.

  O backend atual não oferece revogação de token; `logout()` encerra a sessão
  localmente. O redirecionamento acontece no `finally`.
   ────────────────────────────────────────────────────────────────────────── */

type LogoutButtonProps = {
  variant?: 'rail' | 'header';
  className?: string;
};

export function LogoutButton({ variant = 'header', className = '' }: LogoutButtonProps) {
  const router = useRouter();
  const [isLeaving, setIsLeaving] = useState(false);

  async function handleLogout() {
    if (isLeaving) return;
    setIsLeaving(true);
    try {
      await logout();
    } finally {
      router.replace('/login');
    }
  }

  if (variant === 'rail') {
    return (
      <button
        type="button"
        onClick={handleLogout}
        disabled={isLeaving}
        aria-label="Sair da conta"
        aria-busy={isLeaving}
        title="Sair"
        className={`app-nav__item group relative flex h-11 w-11 items-center justify-center rounded-[12px] border border-transparent transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 active:scale-95 disabled:opacity-60 ${className}`}
      >
        {isLeaving ? (
          <Loader2 aria-hidden="true" size={19} className="animate-spin" />
        ) : (
          <LogOut aria-hidden="true" size={19} strokeWidth={1.6} />
        )}
        <span className="app-nav__tooltip pointer-events-none absolute left-[calc(100%+10px)] top-1/2 z-50 hidden -translate-y-1/2 whitespace-nowrap rounded-lg px-2.5 py-1.5 text-[11px] font-semibold opacity-0 transition-opacity group-hover:block group-hover:opacity-100 group-focus-visible:block group-focus-visible:opacity-100">
          Sair
        </span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      disabled={isLeaving}
      aria-label="Sair da conta"
      aria-busy={isLeaving}
      title="Sair"
      className={`icon-control flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border text-[var(--text-3)] hover:text-[color:var(--status-critico)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] active:scale-95 disabled:opacity-60 ${className}`}
    >
      {isLeaving ? (
        <Loader2 aria-hidden="true" size={16} className="animate-spin" />
      ) : (
        <LogOut aria-hidden="true" size={16} strokeWidth={1.8} />
      )}
    </button>
  );
}

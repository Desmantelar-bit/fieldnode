'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronDown, Loader2, LogOut, Mail, UserRound } from 'lucide-react';
import { getUser, logout, type AuthUser } from '@/services/authService';

/* ──────────────────────────────────────────────────────────────────────────
   UserProfile — identidade da sessão no cabeçalho.

   Onde vive: na barra do topo, nas DUAS larguras (o avatar aparece sempre; o
   primeiro nome só a partir de `sm`, onde há espaço). No desktop o rail
   continua com o seu próprio botão de sair — este menu é o caminho de saída no
   mobile, onde o rail não existe.

   De onde vêm os dados: só da sessão já persistida (`fn-auth-user`, gravada no
   login), lida no cliente depois da montagem. Nenhuma chamada nova ao backend:
   o perfil não precisa de rede para se desenhar, e assim ele funciona offline
   igual ao resto do app.

   O que NÃO é exibido: cargo/papel. O payload de /auth/login/ e /auth/me/
   devolve apenas { id, username, email, first_name, last_name } — não existe
   campo de papel no contrato atual, e inventar um rótulo fixo ("Operador")
   seria afirmar sobre a pessoa algo que a API não disse.
   ────────────────────────────────────────────────────────────────────────── */

/** Iniciais para o avatar: nome+sobrenome, ou as duas primeiras letras do usuário. */
function initialsOf(user: AuthUser | null): string {
  if (!user) return '—';
  const first = user.first_name?.trim() ?? '';
  const last = user.last_name?.trim() ?? '';
  if (first || last) return `${first.charAt(0)}${last.charAt(0)}`.toUpperCase();
  return user.username.slice(0, 2).toUpperCase();
}

/** Nome de exibição: nome completo quando houver, senão o usuário. */
function displayNameOf(user: AuthUser | null): string {
  if (!user) return 'Sessão';
  const full = `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim();
  return full || user.username;
}

export function UserProfile({ className = '' }: { className?: string }) {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [open, setOpen] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  // Só no cliente: a sessão mora em localStorage (o SSR não a enxerga).
  useEffect(() => {
    setUser(getUser());
  }, []);

  // Fecha com clique fora e com Esc — o mínimo que um menu flutuante deve fazer.
  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open]);

  const initials = useMemo(() => initialsOf(user), [user]);
  const name = displayNameOf(user);

  async function handleLogout() {
    if (leaving) return;
    setLeaving(true);
    try {
      await logout();
    } finally {
      // Sempre sai: `logout()` já limpou a sessão local antes de avisar o
      // backend, então nem o servidor fora do ar prende alguém logado aqui.
      router.replace('/login');
    }
  }

  return (
    <div ref={rootRef} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={`Perfil de ${name}`}
        className="profile-chip icon-control flex h-9 items-center gap-2 rounded-xl border pl-1 pr-2.5 text-[var(--text-2)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] active:scale-[0.97]"
      >
        <span className="avatar-tile" aria-hidden="true">{initials}</span>
        <span className="hidden max-w-[7.5rem] truncate text-xs font-semibold sm:block">
          {name}
        </span>
        <ChevronDown
          size={13}
          aria-hidden="true"
          className={`shrink-0 text-[var(--text-3)] transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open ? (
        <div role="menu" aria-label="Perfil do usuário" className="profile-menu">
          <div className="flex items-center gap-3">
            <span className="avatar-tile avatar-tile--lg" aria-hidden="true">{initials}</span>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-[var(--text-1)]">{name}</p>
              <p className="truncate text-[11px] text-[var(--text-3)]">
                {user ? `@${user.username}` : 'sessão ativa'}
              </p>
            </div>
          </div>

          <dl className="mt-3 flex flex-col gap-2 border-t border-[var(--border-subtle)] pt-3">
            <div className="flex items-center gap-2">
              <Mail size={12} className="shrink-0 text-[var(--text-3)]" aria-hidden="true" />
              <dt className="sr-only">E-mail</dt>
              <dd className="min-w-0 truncate text-[11px] text-[var(--text-2)]">
                {user?.email || 'E-mail não cadastrado'}
              </dd>
            </div>
            <div className="flex items-center gap-2">
              <UserRound size={12} className="shrink-0 text-[var(--text-3)]" aria-hidden="true" />
              <dt className="sr-only">Nome de usuário</dt>
              <dd className="min-w-0 truncate text-[11px] text-[var(--text-2)]">
                {user?.username ?? '—'}
              </dd>
            </div>
          </dl>

          <button
            type="button"
            role="menuitem"
            onClick={handleLogout}
            disabled={leaving}
            aria-busy={leaving}
            className="profile-menu__action mt-3 flex w-full items-center justify-center gap-2 rounded-xl border px-3 py-2 text-xs font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--status-critico)] disabled:opacity-60"
          >
            {leaving ? (
              <Loader2 size={13} className="animate-spin" aria-hidden="true" />
            ) : (
              <LogOut size={13} aria-hidden="true" />
            )}
            Sair da conta
          </button>
        </div>
      ) : null}
    </div>
  );
}

'use client';

import Link from 'next/link';
import { FileText, LayoutGrid, Map, Tractor, Users } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { FieldNodeLogo } from '@/components/FieldNodeLogo';
import { LogoutButton } from '@/components/LogoutButton';

// `short` é o rótulo usado na barra inferior do mobile, onde 5 itens disputam
// ~62px de largura cada. `label` continua sendo o texto completo (aria-label e tooltip).
const items = [
  { icon: LayoutGrid, href: '/dashboard',    label: 'Dashboard',  short: 'Início' },
  { icon: Map,         href: '/mapa',         label: 'Mapa',       short: 'Mapa' },
  { icon: Tractor,     href: '/colheitadeiras', label: 'Máquinas', short: 'Frota' },
  { icon: Users,       href: '/operarios',    label: 'Operários',  short: 'Equipe' },
  { icon: FileText,    href: '/relatorios',   label: 'Relatórios', short: 'Relatos' },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <>
      {/* ── Desktop sidebar ── */}
      <nav
        aria-label="Navegação principal"
        className="app-nav app-nav--rail relative z-50 m-4 hidden h-[calc(100vh-2rem)] w-20 shrink-0 flex-col items-center justify-between rounded-[20px] px-2 py-5 lg:flex"
      >
        <FieldNodeLogo className="shrink-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[rgba(255,255,255,0.85)] active:scale-95" />

        {/* Ícones centralizados (horizontal e verticalmente) na pílula flutuante. */}
        <div className="app-nav__cluster flex w-full flex-1 flex-col items-center justify-center gap-1.5">
          {items.map(({ icon: Icon, href, label }) => {
            const isActive = pathname === href || pathname?.startsWith(`${href}/`) === true;
            return (
              <Link
                key={href}
                href={href}
                title={label}
                aria-label={label}
                aria-current={isActive ? 'page' : undefined}
                className={`app-nav__item group relative flex h-11 w-11 items-center justify-center rounded-[12px] border border-transparent transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 active:scale-95 ${
                  isActive ? 'app-nav--active' : ''
                }`}
              >
                <Icon aria-hidden="true" size={19} strokeWidth={isActive ? 2.2 : 1.6} />
                <span className="app-nav__tooltip pointer-events-none absolute left-[calc(100%+10px)] top-1/2 z-50 hidden -translate-y-1/2 whitespace-nowrap rounded-lg px-2.5 py-1.5 text-[11px] font-semibold opacity-0 transition-opacity group-hover:block group-hover:opacity-100 group-focus-visible:block group-focus-visible:opacity-100">
                  {label}
                </span>
              </Link>
            );
          })}
        </div>

        <div className="mt-auto flex w-full flex-col items-center gap-2">
          <LogoutButton variant="rail" />

          <div
            className="app-nav__divider flex w-10 flex-col items-center gap-2 border-t pt-3"
            title="Gateway conectado"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-[color:var(--status-normal)] shadow-[0_0_6px_var(--glow-normal-strong)]" />
            <span className="app-nav__status-label text-[8px] font-semibold uppercase tracking-[0.14em]">
              live
            </span>
          </div>
        </div>
      </nav>

      {/* ── Mobile bottom nav ── */}
      <nav
        aria-label="Navegação mobile"
        className="app-nav app-nav--bar fixed inset-x-3 bottom-[calc(0.75rem+env(safe-area-inset-bottom))] z-50 flex items-center justify-between gap-1 rounded-[1.5rem] px-2 py-1.5 lg:hidden"
      >
        {items.map(({ icon: Icon, href, label, short }) => {
          const isActive = pathname === href || pathname?.startsWith(`${href}/`) === true;
          return (
            <Link
              key={href}
              href={href}
              title={label}
              aria-label={label}
              aria-current={isActive ? 'page' : undefined}
              className={`app-nav__item flex min-h-[3.25rem] min-w-0 flex-1 flex-col items-center justify-center gap-1 rounded-2xl px-0.5 text-[9px] font-semibold transition-all duration-150 min-[400px]:px-1 min-[400px]:text-[10px] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 active:scale-95 ${
                isActive ? 'app-nav--active' : ''
              }`}
            >
              <Icon aria-hidden="true" size={18} strokeWidth={isActive ? 2.2 : 1.6} />
              <span className="max-w-full truncate">{short}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}

'use client';

import Link from 'next/link';
import { FileText, LayoutGrid, Map, Tractor, Users } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { glassPill } from '@/lib/design-tokens';

const items = [
  { icon: LayoutGrid, href: '/dashboard', label: 'Dashboard' },
  { icon: Map, href: '/mapa', label: 'Mapa' },
  { icon: Tractor, href: '/colheitadeiras', label: 'Máquinas' },
  { icon: Users, href: '/operarios', label: 'Operários' },
  { icon: FileText, href: '/relatorios', label: 'Relatórios' },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <>
      <nav
        aria-label="Navegação principal"
        className={`fixed bottom-4 left-4 top-4 z-50 hidden w-20 flex-col items-center justify-between py-5 lg:flex ${glassPill}`}
      >
        <Link
          href="/dashboard"
          aria-label="FieldNode, ir para o dashboard"
          className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent text-sm font-black tracking-tight text-slate-950 shadow-[0_0_22px_var(--glow-normal)] transition hover:scale-105 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent active:scale-[0.97]"
        >
          FN
        </Link>

        <div className="flex flex-col items-center gap-3">
          {items.map(({ icon: Icon, href, label }) => {
            const isActive = pathname === href || pathname.startsWith(`${href}/`);

            return (
              <Link
                key={href}
                href={href}
                title={label}
                aria-label={label}
                aria-current={isActive ? 'page' : undefined}
                className={`group relative rounded-2xl p-3 transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent active:scale-[0.97] ${
                  isActive
                    ? 'bg-accent/10 text-accent shadow-[0_0_15px_var(--glow-normal)]'
                    : 'text-field-text2 hover:bg-white/5 hover:text-field-text1'
                }`}
              >
                <Icon aria-hidden="true" size={21} strokeWidth={1.6} />
                <span className="pointer-events-none absolute left-14 top-1/2 hidden -translate-y-1/2 whitespace-nowrap rounded-lg border border-white/10 bg-slate-950/95 px-2.5 py-1.5 text-[11px] font-semibold text-white opacity-0 shadow-xl transition group-hover:block group-hover:opacity-100">
                  {label}
                </span>
              </Link>
            );
          })}
        </div>

        <div className="flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-field-text3" title="Gateway conectado">
          <span className="h-1.5 w-1.5 rounded-full bg-status-normal shadow-[0_0_8px_var(--glow-normal-strong)]" />
          local
        </div>
      </nav>

      <nav aria-label="Navegação mobile" className="fixed inset-x-3 bottom-3 z-50 flex items-center justify-between gap-1 rounded-3xl border border-white/10 bg-slate-950/90 px-2 py-2 shadow-2xl backdrop-blur-xl lg:hidden">
        {items.map(({ icon: Icon, href, label }) => {
          const isActive = pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              aria-label={label}
              aria-current={isActive ? 'page' : undefined}
              className={`flex min-h-14 flex-1 flex-col items-center justify-center gap-1 rounded-2xl px-1 text-[10px] font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent active:scale-[0.97] ${isActive ? 'bg-accent/10 text-accent' : 'text-field-text3 hover:bg-white/5 hover:text-field-text1'}`}
            >
              <Icon aria-hidden="true" size={19} strokeWidth={1.7} />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}

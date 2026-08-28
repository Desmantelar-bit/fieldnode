'use client';

import Link from 'next/link';
import { FileText, LayoutGrid, Map } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { glassPill } from '@/lib/design-tokens';

const items = [
  { icon: LayoutGrid, href: '/dashboard', label: 'Dashboard' },
  { icon: Map, href: '/mapa', label: 'Máquinas' },
  { icon: FileText, href: '/relatorios', label: 'Relatórios' },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Navegação principal"
      className={`fixed bottom-4 left-4 top-4 z-50 hidden w-20 flex-col items-center justify-center gap-6 lg:flex ${glassPill}`}
    >
      {items.map(({ icon: Icon, href, label }) => {
        const isActive = pathname === href || pathname.startsWith(`${href}/`);

        return (
          <Link
            key={href}
            href={href}
            title={label}
            aria-label={label}
            aria-current={isActive ? 'page' : undefined}
            className={`rounded-full p-3 transition-all duration-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-lime-400 ${
              isActive
                ? 'bg-lime-400/10 text-lime-400 shadow-[0_0_15px_rgba(204,255,0,0.15)]'
                : 'text-slate-400 hover:bg-white/5 hover:text-white'
            }`}
          >
            <Icon aria-hidden="true" size={22} strokeWidth={1.5} />
          </Link>
        );
      })}
    </nav>
  );
}

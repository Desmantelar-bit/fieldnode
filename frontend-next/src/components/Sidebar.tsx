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
  const renderItem = ({ icon: Icon, href, label }: (typeof items)[number], mobile = false) => {
    const isActive = pathname === href || pathname.startsWith(`${href}/`);
    return (
      <Link
        key={href}
        href={href}
        title={label}
        aria-label={label}
        aria-current={isActive ? 'page' : undefined}
        className={`${mobile ? 'flex min-h-16 flex-1 flex-col items-center justify-center gap-1 px-1 py-2 text-[10px]' : 'rounded-full p-3'} transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${isActive ? 'bg-accent/10 text-accent shadow-[0_0_18px_rgba(204,255,0,0.15)]' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
      >
        <Icon aria-hidden="true" size={mobile ? 20 : 22} strokeWidth={1.6} />
        {mobile ? <span>{label}</span> : null}
      </Link>
    );
  };

  return (
    <>
      <nav aria-label="Navegação principal" className={`fixed bottom-4 left-4 top-4 z-50 hidden w-20 flex-col items-center justify-center gap-4 lg:flex ${glassPill}`}>
        {items.map((item) => renderItem(item))}
      </nav>
      <nav aria-label="Navegação mobile" className="fixed inset-x-3 bottom-3 z-50 flex gap-1 rounded-2xl border border-white/10 bg-slate-950/85 px-1 py-1 shadow-glass backdrop-blur-xl lg:hidden">
        {items.map((item) => renderItem(item, true))}
      </nav>
    </>
  );
}

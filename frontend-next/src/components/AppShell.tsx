import Link from 'next/link';
import type { ReactNode } from 'react';

type NavItem = {
  href: string;
  label: string;
  icon: string;
};

const navItems: NavItem[] = [
  { href: '/dashboard', label: 'Dashboard', icon: 'grid' },
  { href: '/colheitadeiras', label: 'Maquinas', icon: 'machine' },
  { href: '/operarios', label: 'Operarios', icon: 'users' },
];

const icons: Record<string, ReactNode> = {
  grid: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
    </svg>
  ),
  machine: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 15h11l2-5h3v5" />
      <path d="M5 15v-4h5l2 4" />
      <circle cx="7" cy="17" r="2" />
      <circle cx="18" cy="17" r="2" />
    </svg>
  ),
  users: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" />
      <circle cx="9.5" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  ),
};

export function AppShell({
  active,
  title,
  eyebrow,
  actions,
  children,
}: {
  active: string;
  title: string;
  eyebrow?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(100,217,140,0.12),transparent_34rem),linear-gradient(180deg,#0b100e,#070a09)] text-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-white/10 bg-black/20 px-4 py-5 backdrop-blur-xl lg:flex lg:flex-col">
        <Link href="/dashboard" className="mb-6 flex items-center gap-3 border-b border-white/10 px-2 pb-5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-emerald-300/25 bg-emerald-300/10 text-emerald-200">
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2 3 7l9 5 9-5-9-5Z" />
              <path d="m3 12 9 5 9-5" />
              <path d="m3 17 9 5 9-5" />
            </svg>
          </span>
          <span>
            <span className="block text-sm font-semibold tracking-tight">FieldNode</span>
            <span className="block text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">Telemetria</span>
          </span>
        </Link>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const isActive = active === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition ${
                  isActive
                    ? 'bg-emerald-300/10 text-emerald-200 ring-1 ring-emerald-300/20'
                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-100'
                }`}
              >
                <span className="h-4 w-4">{icons[item.icon]}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto rounded-lg border border-white/10 bg-white/[0.03] p-3">
          <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">
            <span className="h-2 w-2 rounded-full bg-emerald-300 shadow-[0_0_14px_rgba(110,231,183,0.7)]" />
            API online
          </div>
          <p className="mt-2 text-xs text-slate-500">127.0.0.1:8000/api</p>
        </div>
      </aside>

      <section className="lg:pl-64">
        <header className="sticky top-0 z-20 border-b border-white/10 bg-[#090d0b]/80 px-4 py-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
            <div>
              {eyebrow ? <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-emerald-200/80">{eyebrow}</p> : null}
              <h1 className="mt-1 text-xl font-semibold tracking-tight text-slate-50 sm:text-2xl">{title}</h1>
            </div>
            {actions}
          </div>
        </header>

        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</div>
      </section>
    </main>
  );
}

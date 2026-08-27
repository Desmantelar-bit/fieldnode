import Link from 'next/link';
import type { ReactNode } from 'react';
import { resolveApiUrl } from "@/services/telemetryService";
import { ApiStatusIndicator } from "@/components/ApiStatusIndicator";

type NavItem = {
  href: string;
  label: string;
  icon: string;
};

const navItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: "grid" },
  { href: "/mapa", label: "Mapa", icon: "map" },
  { href: "/colheitadeiras", label: "Máquinas", icon: "machine" },
  { href: "/operarios", label: "Operários", icon: "users" },
  { href: "/relatorios", label: "Relatórios", icon: "report" },
];

const API_URL = resolveApiUrl();

const icons: Record<string, ReactNode> = {
  grid: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
    </svg>
  ),
  map: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7z" />
      <circle cx="12" cy="9" r="2.5" />
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
  report: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
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
    <main className="min-h-screen bg-[image:var(--surface-page)] text-field-text">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-field-border bg-black/20 px-4 py-6 backdrop-blur-xl lg:flex lg:flex-col">
        <Link
          href="/dashboard"
          className="mb-6 flex items-center gap-3 border-b border-field-border px-2 pb-6"
        >
          <span className="flex h-9 w-9 items-center justify-center border border-accent/25 bg-accent/10 text-accent">
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2 3 7l9 5 9-5-9-5Z" />
              <path d="m3 12 9 5 9-5" />
              <path d="m3 17 9 5 9-5" />
            </svg>
          </span>
          <span>
            <span className="block text-sm font-semibold tracking-tight">
              FieldNode
            </span>
            <span className="block text-[10px] font-semibold uppercase tracking-label text-field-text3">
              Telemetria
            </span>
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
                    ? "bg-accent/10 text-accent ring-1 ring-accent/20"
                    : "text-field-text3 hover:bg-field-glass-strong hover:text-field-text2"
                }`}
              >
                <span className="h-4 w-4">{icons[item.icon]}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto border border-field-border bg-field-glass p-3">
          <ApiStatusIndicator />
          <p className="mt-2 text-xs text-field-text3">{API_URL}</p>
        </div>
      </aside>

      <section className="lg:pl-64 pb-24 lg:pb-0">
        <header className="sticky top-0 z-20 border-b border-field-border bg-[color:var(--surface-header)] px-4 py-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
            <div>
              {eyebrow ? (
                <p className="text-[11px] font-semibold uppercase tracking-label text-accent/80">
                  {eyebrow}
                </p>
              ) : null}
              <h1 className="mt-1 text-xl font-semibold tracking-title text-field-text1 sm:text-2xl">
                {title}
              </h1>
            </div>
            {actions}
          </div>
        </header>

        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {children}
        </div>
      </section>

      {/* Mobile bottom navigation */}
      <nav className="fixed inset-x-0 bottom-0 z-30 flex items-center justify-between gap-2 bg-black/80 border-t border-field-border px-4 py-3 backdrop-blur-xl lg:hidden">
        {navItems.map((item) => {
          const isActive = active === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex min-h-[4rem] w-full flex-col items-center justify-center px-3 py-3 text-xs font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
                isActive
                  ? "text-accent"
                  : "text-field-text2 hover:text-field-text1"
              }`}
              aria-label={item.label}
            >
              <span className="h-6 w-6">{icons[item.icon]}</span>
              <span className="mt-1 block text-[11px]">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </main>
  );
}

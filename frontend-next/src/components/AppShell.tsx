import type { ReactNode } from 'react';
import { BackButton } from '@/components/BackButton';
import { Sidebar } from '@/components/Sidebar';

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
  const showBackButton = active !== '/dashboard';

  return (
    <main className="min-h-screen bg-[image:var(--surface-page)] text-field-text">
      <Sidebar />
      {showBackButton ? <BackButton /> : null}

      <section className="pb-24 lg:ml-28 lg:pb-0">
        <header className="sticky top-0 z-20 border-b border-field-border bg-[color:var(--surface-header)] px-4 py-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
            <div className={showBackButton ? 'pl-14 lg:pl-0' : ''}>
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
    </main>
  );
}

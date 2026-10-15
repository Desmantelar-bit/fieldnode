import type { ReactNode } from 'react';
import { BackButton } from '@/components/BackButton';
import { Sidebar } from '@/components/Sidebar';
import { SessionGate } from '@/components/SessionGate';
import { ThemeToggle } from '@/components/ThemeToggle';
import { UserProfile } from '@/components/UserProfile';
import { ApiStatusIndicator } from '@/components/ApiStatusIndicator';

/**
 * AppShell — o chrome compartilhado das rotas do app.
 *
 * Tudo aqui dentro é envolvido por `SessionGate`, então a exigência de sessão
 * vale para todas as páginas de uma só vez (ver SessionGate para o que essa
 * guarda garante e o que ela não garante).
 */
export function AppShell({
  active,
  title,
  eyebrow,
  description,
  actions,
  titleSlot,
  contentClassName = '',
  children,
}: {
  active: string;
  title: string;
  eyebrow?: string;
  description?: string;
  actions?: ReactNode;
  /**
   * Substitui o bloco eyebrow + título + descrição no cabeçalho. Usado no
   * dashboard para colocar o logotipo horizontal do FieldNode no lugar do
   * título — o `title` continua obrigatório para o nome acessível.
   */
  titleSlot?: ReactNode;
  contentClassName?: string;
  children: ReactNode;
}) {
  const showBackButton = active !== '/dashboard';

  return (
    <SessionGate>
      <main className="app-background flex h-screen w-screen overflow-hidden text-[var(--foreground)]">
        <Sidebar />

        <section className="relative z-10 flex h-screen min-w-0 flex-1 flex-col overflow-hidden bg-transparent">
          <header className="w-full shrink-0 bg-transparent px-6 pt-6 pb-4 lg:px-8">
            <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-x-4 gap-y-2">
              <div className="flex min-w-0 items-center gap-3">
                {showBackButton ? <BackButton /> : null}
                {titleSlot ? (
                  <div className="min-w-0" role="img" aria-label={title}>
                    {titleSlot}
                  </div>
                ) : (
                  <div className="min-w-0">
                    {eyebrow ? (
                      <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]">
                        {eyebrow}
                      </p>
                    ) : null}
                    <h1 className="mt-0.5 text-2xl font-bold tracking-tight text-[var(--text-1)] sm:text-3xl">
                      {title}
                    </h1>
                    {description ? (
                      <p className="mt-0.5 hidden text-xs text-[var(--text-3)] sm:block">{description}</p>
                    ) : null}
                  </div>
                )}
              </div>

              <div className="flex min-w-0 max-w-full shrink items-center gap-2">
                <div className="hidden sm:block">
                  <ApiStatusIndicator />
                </div>
                {actions}
                {/* Perfil da sessão. No mobile ele é também o caminho de saída,
                    porque o menu traz "Sair da conta" e o rail não existe lá;
                    no desktop a saída continua no pé do rail. Um só lugar de
                    cada vez — nunca dois botões de sair no mesmo cabeçalho. */}
                <UserProfile />
                <ThemeToggle />
              </div>
            </div>
          </header>

          <div className="app-content min-h-0 flex-1 overflow-y-auto">
            <div className={`mx-auto w-full max-w-7xl px-6 py-6 lg:px-8 ${contentClassName}`}>
              {children}
            </div>
          </div>
        </section>
      </main>
    </SessionGate>
  );
}

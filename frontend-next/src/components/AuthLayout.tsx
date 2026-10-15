import type { ReactNode } from 'react';

/* ──────────────────────────────────────────────────────────────────────────
   AuthLayout — o palco compartilhado de /login e /register.

   A foto de marca ocupa a tela inteira, com um véu escuro por cima para
   garantir contraste; o formulário é um único card de VIDRO FOSCO centralizado
   (o desenho do card está em `.auth-card`, no globals.css).

   Não há mais painel de marca separado: a identidade vive dentro do próprio
   card (o lockup horizontal com a assinatura, renderizado pelas páginas) e a
   frase de impacto virou legenda de canto, visível só em telas largas.
   ────────────────────────────────────────────────────────────────────────── */

type AuthLayoutProps = {
  children: ReactNode;
  /** Frase de marca exibida como legenda de canto (telas largas). */
  headline?: ReactNode;
};

export function AuthLayout({ children, headline }: AuthLayoutProps) {
  return (
    <div className="auth-stage">
      {/* Foto e véu são puramente decorativos: saem da árvore de acessibilidade. */}
      <div className="auth-stage__photo" aria-hidden="true" />
      <div className="auth-stage__veil" aria-hidden="true" />

      <main className="auth-panel">{children}</main>

      {headline ? <p className="auth-stage__caption">{headline}</p> : null}
    </div>
  );
}

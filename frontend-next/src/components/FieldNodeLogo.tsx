import Link from 'next/link';

/* ──────────────────────────────────────────────────────────────────────────
   FieldNodeLogo — a marca tipográfica do FieldNode.

   Composição (igual às duas versões do logo enviadas pelo cliente):
     "Field" em Snippet — geométrica, com os terminais curvos do 'l' e do 'd';
     "NODE"  em Staatliches, chapado em lima (sem textura).

   Duas variantes:
     · `stacked`    — "Field" sobre "NODE". Vive dentro do rail, cujo chrome é
                      PRETO nos dois temas, então a tinta do "Field" é clara.
                      Sem chip, sem borda e sem glow: a marca se apoia direto
                      no preto do rail.
     · `horizontal` — lockup lado a lado com a assinatura "Telemetria para
                      Máquinas Agrícolas" sob o NODE. Vive direto sobre o fundo
                      da página (título do dashboard e tela de login), então a
                      tinta do "Field" segue o tema: branca no escuro, grafite
                      no claro.

   O desenho todo mora em globals.css (bloco "LOGO FIELDNODE"); aqui só existe
   a estrutura, para a marca ser reutilizável e ter um só lugar de verdade.
   ────────────────────────────────────────────────────────────────────────── */

/** Assinatura padrão da marca, usada na variante horizontal. */
export const BRAND_TAGLINE = 'Telemetria para Máquinas Agrícolas';

type FieldNodeLogoProps = {
  variant?: 'stacked' | 'horizontal';
  /** Classe extra para ajustes de layout do ponto de uso. */
  className?: string;
  /** Quando false, não envolve em <Link> (uso em cabeçalho, já dentro do app). */
  asLink?: boolean;
  /** Texto do aria-label; só é usado na variante com link. */
  label?: string;
  /**
   * Assinatura exibida sob o NODE na variante horizontal.
   *
   * O padrão é `null` — SEM assinatura. Um logotipo que vai para o cabeçalho de
   * uma página precisa ser curto, e a linha "Telemetria para Máquinas
   * Agrícolas" só entra onde há espaço e vontade explícita (a tela de login).
   * Passe `BRAND_TAGLINE` para exibi-la.
   */
  tagline?: string | null;
};

export function FieldNodeLogo({
  variant = 'stacked',
  className = '',
  asLink = true,
  label = 'FieldNode — ir para o dashboard',
  tagline = null,
}: FieldNodeLogoProps) {
  const isHorizontal = variant === 'horizontal';
  const showTagline = isHorizontal && Boolean(tagline);

  const classes = [
    'fieldnode-logo',
    isHorizontal ? 'fieldnode-logo--horizontal' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const mark = (
    <>
      <span className="fieldnode-logo__mark" aria-hidden="true">
        <span className="fieldnode-logo__field">Field</span>
        {/* O NODE e a assinatura formam uma coluna para o texto ficar ancorado
            na largura do próprio NODE, como no logo de referência. */}
        <span className="fieldnode-logo__nodecol">
          <span className="fieldnode-logo__node">NODE</span>
          {showTagline ? <span className="fieldnode-logo__tagline">{tagline}</span> : null}
        </span>
      </span>
      {/* O nome acessível da marca, uma vez só, independente da variante. */}
      <span className="sr-only">
        FieldNode{showTagline ? ` — ${tagline}` : ''}
      </span>
    </>
  );

  if (!asLink) {
    return <span className={classes}>{mark}</span>;
  }

  return (
    <Link href="/dashboard" aria-label={label} className={classes}>
      {mark}
    </Link>
  );
}

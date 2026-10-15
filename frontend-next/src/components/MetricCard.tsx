import type { ReactNode } from 'react';

// A cor do valor vem do modificador `.stat-value--*`, e não de uma utility do
// Tailwind: `.stat-value` mora em CSS não-layerizado, que vence qualquer
// `@layer utilities`. Utilities de cor como as de status eram, por isso,
// ignoradas, e todos os números saíam brancos — invisíveis nos cards claros.
// `.metric-card--*` continua sendo aplicado porque carrega o glow de tom.
const toneValueClass = {
  emerald: 'stat-value--normal',
  amber:   'stat-value--atencao',
  red:     'stat-value--critico',
  slate:   '',
} as const;

export function MetricCard({
  label,
  value,
  helper,
  tone = 'slate',
}: {
  label: string;
  value: ReactNode;
  helper?: string;
  tone?: keyof typeof toneValueClass;
}) {
  return (
    /* Conteúdo CENTRADO e altura mínima comum: numa linha de três ou quatro
       cards, o rótulo de cima e a legenda de baixo variavam de altura conforme o
       texto, e os números saíam em alturas diferentes de um card para o outro.
       Com o miolo centrado e a mesma altura, a linha de números fica alinhada —
       que é o que dá o ar de conjunto em vez de quatro caixas soltas. */
    <article
      role="group"
      aria-label={label}
      className={`metric-card metric-card--${tone} flex min-h-[8.75rem] flex-col items-center justify-center text-center`}
    >
      <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
        {label}
      </p>
      <div className={`stat-value mt-3 text-3xl font-bold sm:text-4xl ${toneValueClass[tone]}`}>
        {value}
      </div>
      {helper ? (
        <p className="mt-2 text-xs text-[var(--text-3)]">{helper}</p>
      ) : null}
    </article>
  );
}

'use client';

import { useEffect, useMemo, useState } from 'react';

/* ──────────────────────────────────────────────────────────────────────────
   OperationClock — o relógio da operação, com mostrador radial.

   Por que existe: a distribuição operacional passou a dividir a linha com um
   painel de contexto. O relógio é o dado de contexto mais honesto que existe —
   é o horário real do navegador do operador, não um número inventado para
   preencher espaço.

   O mostrador: 60 marcas, uma por minuto da hora corrente. As já passadas ficam
   em lima e as restantes apagadas, então o anel é a hora atual lida como
   progresso — o mesmo motivo do mostrador da referência.

   Sobre a temperatura de ambiente: o backend já devolve temperatura e umidade
   dentro de cada colheitadeira, mas o schema do frontend descarta o campo.
   Exibir esse dado exige alterar o schema, o que está fora do escopo autorizado
   — por isso este painel mostra só o horário, por enquanto.
   ────────────────────────────────────────────────────────────────────────── */

const TICKS = 60;

export function OperationClock({ className = '' }: { className?: string }) {
  const [now, setNow] = useState<Date | null>(null);

  // Só no cliente: o servidor não conhece o relógio de quem abre a página, e
  // renderizar a hora no SSR daria divergência de hidratação.
  useEffect(() => {
    setNow(new Date());
    const id = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const minute = now ? now.getMinutes() : 0;

  // As marcas só são recalculadas quando o MINUTO muda; o relógio re-renderiza
  // a cada segundo apenas para o mostrador, não para reconstruir o anel.
  const ticks = useMemo(
    () =>
      Array.from({ length: TICKS }, (_, index) => ({
        index,
        angle: (index / TICKS) * 360 - 90,
        passou: index <= minute,
      })),
    [minute],
  );

  const hora = now
    ? now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    : '--:--';

  const dataPorExtenso = now
    ? now.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' })
    : '';

  return (
    <section
      aria-label="Horário da operação"
      className={`metric-card flex flex-col items-center justify-center text-center ${className}`}
    >
      <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]">
        Operação agora
      </p>

      <div className="relative mt-3 h-32 w-32 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full" aria-hidden="true">
          {ticks.map(({ index, angle, passou }) => {
            const marco = index % 5 === 0;
            return (
              <line
                key={index}
                x1="50"
                y1="5"
                x2="50"
                y2={marco ? 13 : 10}
                transform={`rotate(${angle} 50 50)`}
                stroke={passou ? 'var(--lime)' : 'var(--border-highlight)'}
                strokeWidth={marco ? 2.6 : 1.3}
                strokeLinecap="round"
              />
            );
          })}
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center gap-0.5">
          <p className="stat-value text-3xl font-bold text-[var(--text-1)]">{hora}</p>
          <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-[var(--text-3)]">
            horário local
          </p>
        </div>
      </div>

      {now ? (
        <time
          dateTime={now.toISOString()}
          className="mt-3 text-xs text-[var(--text-2)]"
        >
          {dataPorExtenso.charAt(0).toUpperCase() + dataPorExtenso.slice(1)}
        </time>
      ) : (
        <p className="mt-3 text-xs text-[var(--text-3)]">—</p>
      )}
    </section>
  );
}

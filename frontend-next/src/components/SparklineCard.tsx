'use client';

import { Line, LineChart, ResponsiveContainer } from 'recharts';
import { glassCard, kpiLabel, kpiNumber, sparklineColor } from '@/lib/design-tokens';

type SparklineStatus = 'normal' | 'atencao' | 'critico';

interface SparklineCardProps {
  titulo: string;
  valor: string | number;
  unidade?: string;
  dados: { valor: number }[];
  status: SparklineStatus;
}

export function SparklineCard({
  titulo,
  valor,
  unidade,
  dados,
  status,
}: SparklineCardProps) {
  const critico = status === 'critico';

  return (
    <article
      aria-label={titulo}
      className={`${glassCard} relative overflow-hidden p-6 transition-all duration-300 hover:border-white/20 ${
        critico
          ? 'border-orange-500/30 bg-gradient-to-br from-orange-950/40 via-slate-900/40 to-slate-900/40 shadow-[0_0_30px_rgba(255,94,0,0.15)]'
          : ''
      }`}
    >
      <p className={kpiLabel}>{titulo}</p>
      <p className={kpiNumber}>
        {valor}
        {unidade ? <span className="ml-1 text-lg font-normal text-slate-400">{unidade}</span> : null}
      </p>
      <div className="mt-4 h-12 opacity-80" aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={dados}>
            <Line
              type="monotone"
              dataKey="valor"
              stroke={sparklineColor[status]}
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}

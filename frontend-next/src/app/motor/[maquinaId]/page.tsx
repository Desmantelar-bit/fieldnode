'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Activity, ArrowLeft, ShieldAlert } from 'lucide-react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/EmptyState';
import { LoadingState } from '@/components/ui/FeedbackStates';
import { StatusBadge } from '@/components/StatusBadge';
import { telemetryService } from '@/services/telemetryService';
import type { CanMotorResponse, CanReading } from '@/schemas/canMotor';

const metricSpecs: {
  field: keyof CanReading;
  label: string;
  unit: string;
  color: string;
}[] = [
  { field: 'oleo_pressao_kpa', label: 'Pressão do óleo', unit: 'kPa', color: 'var(--chart-blue-stroke)' },
  { field: 'oleo_temp_c', label: 'Temperatura do óleo', unit: '°C', color: 'var(--chart-atencao-stroke)' },
  { field: 'liquido_temp_c', label: 'Temperatura do líquido', unit: '°C', color: 'var(--chart-critico-stroke)' },
  { field: 'rail_pressao_kpa', label: 'Pressão do rail', unit: 'kPa', color: 'var(--chart-violet-stroke)' },
  { field: 'turbo_pressao_kpa', label: 'Pressão do turbo', unit: 'kPa', color: 'var(--chart-normal-stroke)' },
  { field: 'escape_temp_c', label: 'Temperatura de escape', unit: '°C', color: 'var(--chart-blue-stroke)' },
];

const subsystemLabels: Record<string, string> = {
  arrefecimento: 'Arrefecimento',
  lubrificacao: 'Lubrificação',
  combustivel_alta_pressao: 'Combustível de alta pressão',
  admissao: 'Admissão',
};

function toneForStatus(status: string | null): 'normal' | 'warning' | 'critical' | 'muted' {
  if (status === 'NORMAL') return 'normal';
  if (status === 'ATENCAO') return 'warning';
  if (status === 'CRITICO') return 'critical';
  return 'muted';
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  return Number.isNaN(date.getTime()) ? timestamp : date.toLocaleTimeString('pt-BR');
}

function CounterList({ title, counts }: { title: string; counts: Record<string, number> }) {
  const entries = Object.entries(counts).filter(([, count]) => count > 0);
  if (!entries.length) return null;
  return (
    <div>
      <h3 className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">{title}</h3>
      <ul className="mt-2 flex flex-wrap gap-2">
        {entries.map(([key, count]) => (
          <li key={key} className="rounded-lg bg-[var(--panel-glass-mid)] px-2.5 py-1.5 text-[10px] text-[var(--text-2)]">
            {key.replaceAll('_', ' ')} <strong className="ml-1 text-[var(--text-1)]">{count}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MetricChart({
  reading,
  field,
  label,
  unit,
  color,
}: {
  reading: CanReading[];
  field: keyof CanReading;
  label: string;
  unit: string;
  color: string;
}) {
  const points = reading.filter((item) => typeof item[field] === 'number');
  const latest = points.at(-1)?.[field];
  return (
    <article className="metric-card min-w-0">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold text-[var(--text-2)]">{label}</h3>
          <p className="mt-1 text-lg font-bold text-[var(--text-1)]">
            {typeof latest === 'number' ? `${latest.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} ${unit}` : 'Sem leitura'}
          </p>
        </div>
        <Activity size={15} aria-hidden="true" className="mt-1 shrink-0 text-[var(--text-3)]" />
      </div>
      {points.length < 2 ? (
        <p className="mt-5 rounded-lg bg-[var(--panel-glass-mid)] px-3 py-4 text-xs text-[var(--text-3)]">
          {points.length === 0 ? 'Nenhuma leitura válida para este sinal.' : 'Aguardando mais uma leitura para exibir tendência.'}
        </p>
      ) : (
        <div className="mt-3 h-44 w-full" role="img" aria-label={`Gráfico de ${label}, ${points.length} leituras`}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 8, right: 10, bottom: 14, left: -8 }}>
              <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatTime}
                tick={{ fill: 'var(--text-3)', fontSize: 9 }}
                minTickGap={24}
                axisLine={{ stroke: 'var(--line)' }}
                tickLine={false}
                label={{ value: 'Horário', position: 'insideBottomRight', offset: -4, style: { fill: 'var(--text-3)', fontSize: 9 } }}
              />
              <YAxis
                width={48}
                tick={{ fill: 'var(--text-3)', fontSize: 9 }}
                axisLine={false}
                tickLine={false}
                domain={['auto', 'auto']}
                label={{ value: unit, angle: -90, position: 'insideLeft', offset: 8, style: { fill: 'var(--text-3)', fontSize: 9 } }}
              />
              <Tooltip
                labelFormatter={(value) => formatTime(String(value))}
                formatter={(value) => [`${Number(value).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} ${unit}`, label]}
                contentStyle={{ background: 'var(--surface-card)', border: '1px solid var(--line)', borderRadius: 12, color: 'var(--text-1)', fontSize: 11 }}
              />
              <Line type="monotone" dataKey={field} name={label} stroke={color} strokeWidth={2} dot={false} activeDot={{ r: 4 }} connectNulls={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      <p className="mt-1 text-[10px] text-[var(--text-3)]">{points.length} leituras válidas · últimos dados</p>
    </article>
  );
}

export default function MotorCANPage() {
  const params = useParams<{ maquinaId: string }>();
  const maquinaId = params?.maquinaId ?? '';
  const [data, setData] = useState<CanMotorResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  const load = useCallback(async (silent: boolean, isCurrent: () => boolean) => {
    if (!maquinaId) return;
    if (isCurrent()) {
      if (silent) setRefreshing(true);
      else setLoading(true);
    }
    try {
      const next = await telemetryService.getMotorCAN(maquinaId);
      if (!isCurrent()) return;
      setData(next);
      setError(null);
      setUpdatedAt(new Date());
    } catch (reason: unknown) {
      if (!isCurrent()) return;
      setError(reason instanceof Error ? reason.message : 'Falha ao carregar o módulo CAN.');
    } finally {
      if (isCurrent()) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, [maquinaId]);

  useEffect(() => {
    if (!maquinaId) {
      setLoading(false);
      return;
    }
    let active = true;
    let timeout: ReturnType<typeof setTimeout> | undefined;
    const poll = async (silent: boolean) => {
      await load(silent, () => active);
      if (active) timeout = setTimeout(() => { void poll(true); }, 5000);
    };
    void poll(false);
    return () => {
      active = false;
      if (timeout) clearTimeout(timeout);
    };
  }, [maquinaId, load]);

  const prescriptions = useMemo(
    () => [...(data?.prescricoes ?? [])].sort((a, b) => {
      const order = { CRITICO: 0, ATENCAO: 1, NORMAL: 2 } as const;
      return (order[a.status as keyof typeof order] ?? 3) - (order[b.status as keyof typeof order] ?? 3);
    }),
    [data?.prescricoes],
  );

  if (!maquinaId) {
    return <AppShell active="/colheitadeiras" eyebrow="Módulo CAN" title="Máquina não selecionada"><EmptyState title="Selecione uma máquina." message="Abra o módulo Motor a partir da tela de detalhes da máquina." /></AppShell>;
  }

  if (loading && !data) {
    return <AppShell active="/colheitadeiras" eyebrow="Módulo CAN · Motor" title={`Máquina ${maquinaId}`}><LoadingState mensagem="Carregando telemetria CAN do motor..." /></AppShell>;
  }

  if (!data && error) {
    return <AppShell active="/colheitadeiras" eyebrow="Módulo CAN · Motor" title={`Máquina ${maquinaId}`}><ErrorState title="Não foi possível carregar a telemetria CAN." message={error} /></AppShell>;
  }

  if (!data) return null;

  const lastReading = data.ultima_leitura;
  const qualityPercent = data.qualidade.recebidas > 0
    ? Math.round((data.qualidade.aceitas / data.qualidade.recebidas) * 100)
    : null;

  return (
    <AppShell
      active="/colheitadeiras"
      eyebrow="Módulo CAN · Motor"
      title={`Máquina ${maquinaId}`}
      description="Telemetria, qualidade dos dados e prescrições explicáveis por subsistema."
      actions={(
        <Link href={`/detalhes?id=${encodeURIComponent(maquinaId)}`} className="inline-flex items-center gap-2 rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] px-3 py-2 text-xs font-semibold text-[var(--text-2)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)]">
          <ArrowLeft size={13} aria-hidden="true" /> Detalhes
        </Link>
      )}
    >
      <div className="space-y-5">
        {(data.simulado || data.origem_dados === 'MISTO') && (
          <section className="flex items-start gap-3 rounded-2xl border border-[color:var(--status-atencao)]/30 bg-[color:var(--status-atencao)]/8 px-4 py-3" aria-label="Aviso de dados simulados">
            <ShieldAlert size={17} aria-hidden="true" className="mt-0.5 shrink-0 text-[color:var(--status-atencao)]" />
            <div>
              <p className="text-xs font-bold text-[color:var(--status-atencao)]">
                {data.origem_dados === 'MISTO' ? 'DADOS REAIS E SIMULADOS' : 'DADOS SIMULADOS'}
              </p>
              <p className="mt-1 text-[11px] leading-relaxed text-[var(--text-2)]">
                {data.origem_dados === 'MISTO'
                  ? 'A série mistura registros simulados e não simulados. Confira a origem de cada leitura antes de interpretar.'
                  : 'A série foi gerada para demonstração; não representa condição de campo nem deve orientar manutenção real.'}
              </p>
            </div>
          </section>
        )}

        {error && (
          <p className="rounded-xl border border-[color:var(--status-atencao)]/25 bg-[color:var(--status-atencao)]/6 px-3 py-2 text-xs text-[var(--text-2)]" role="status">
            Atualização indisponível; mantendo a última resposta recebida. {error}
          </p>
        )}

        <section aria-labelledby="prescriptions-title" className="space-y-3">
          <div>
            <h2 id="prescriptions-title" className="text-lg font-bold text-[var(--text-1)]">Prescrições por subsistema</h2>
            <p className="mt-1 text-xs text-[var(--text-3)]">Regras determinísticas explicáveis; evidência baixa ou dado ausente não é tratado como normalidade confirmada.</p>
          </div>
          <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
            {prescriptions.map((item) => (
              <article key={item.subsistema} className="metric-card space-y-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <h3 className="text-sm font-bold text-[var(--text-1)]">{subsystemLabels[item.subsistema] ?? item.subsistema}</h3>
                    <p className="mt-1 text-[10px] text-[var(--text-3)]">Evidência {item.evidencia_nivel.toLocaleLowerCase('pt-BR')}</p>
                  </div>
                  <StatusBadge tone={toneForStatus(item.status)}>{item.status ?? 'Sem dados'}</StatusBadge>
                </div>
                <p className="text-xs leading-relaxed text-[var(--text-2)]">{item.diagnostico}</p>
                <div className="rounded-xl bg-[var(--panel-glass-mid)] p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">Ação sugerida · {item.prazo}</p>
                  <p className="mt-1.5 text-xs leading-relaxed text-[var(--text-1)]">{item.acao}</p>
                </div>
                <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[var(--line)] pt-3">
                  <p className="text-xs text-[var(--text-2)]">Horas de motor até o limite: <strong className="text-[var(--text-1)]">{item.horas_ate_limite === null ? 'Sem estimativa' : `${item.horas_ate_limite} h`}</strong></p>
                  <p className="max-w-full text-right text-[10px] leading-relaxed text-[var(--text-3)]">{item.motivo_estimativa}</p>
                </div>
                {item.limite_referencia && (
                  <p className="text-[10px] leading-relaxed text-[var(--text-3)]">
                    Limite usado: {item.limite_referencia.sinal.replaceAll('_', ' ')} {item.limite_referencia.direcao} {item.limite_referencia.valor} {item.limite_referencia.unidade}. {item.limite_referencia.origem}
                  </p>
                )}
                {item.sinais_usados.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {item.sinais_usados.map((signal) => (
                      <span key={signal.sinal} className="rounded-lg border border-[var(--line)] px-2 py-1 text-[10px] text-[var(--text-2)]">
                        {signal.sinal.replaceAll('_', ' ')}: {signal.valor} {signal.unidade}{signal.concorda ? ' · concordante' : ''}
                      </span>
                    ))}
                  </div>
                )}
                {item.sinais_indisponiveis.length > 0 && (
                  <p className="text-[10px] text-[var(--text-3)]">Sinais indisponíveis: {item.sinais_indisponiveis.join(', ')}.</p>
                )}
                {item.dtcs_relacionados.map((dtc) => (
                  <p key={`${dtc.spn}-${dtc.fmi}`} className="text-[10px] text-[var(--text-3)]">DTC de referência relacionado: SPN {dtc.spn} · FMI {dtc.fmi} — {dtc.descricao_referencia}</p>
                ))}
              </article>
            ))}
          </div>
        </section>

        <section aria-labelledby="dtc-title" className="space-y-3">
          <div>
            <h2 id="dtc-title" className="text-lg font-bold text-[var(--text-1)]">Códigos de falha (DTC)</h2>
            <p className="mt-1 text-xs text-[var(--text-3)]">Descrições são referências de aplicação e podem variar por fabricante e motor.</p>
          </div>
          {data.dtcs_ativos.length === 0 ? (
            <div className="metric-card py-5 text-xs text-[var(--text-3)]">Nenhum DTC ativo recebido.</div>
          ) : (
            <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
              {data.dtcs_ativos.map((dtc) => (
                <article key={`${dtc.spn}-${dtc.fmi}`} className="metric-card border border-[var(--line)]">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="font-mono text-sm font-bold text-[var(--text-1)]">SPN {dtc.spn} · FMI {dtc.fmi}</h3>
                    <div className="flex items-center gap-2">
                      {dtc.simulado && <StatusBadge tone="warning">Simulado</StatusBadge>}
                      <StatusBadge tone={dtc.ativo ? 'critical' : 'muted'}>{dtc.ativo ? 'Ativo' : 'Inativo'}</StatusBadge>
                    </div>
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-[var(--text-2)]">{dtc.descricao_referencia ?? 'Sem descrição de referência cadastrada.'}</p>
                  <p className="mt-2 text-[10px] text-[var(--text-3)]">Subsistema: {subsystemLabels[dtc.subsistema] ?? dtc.subsistema} · ocorrências: {dtc.ocorrencias}</p>
                  <p className="mt-1 text-[10px] text-[var(--text-3)]">Primeira ocorrência: {new Date(dtc.primeira_vez).toLocaleString('pt-BR')}</p>
                  <p className="mt-1 text-[10px] text-[var(--text-3)]">Última ocorrência: {new Date(dtc.ultima_vez).toLocaleString('pt-BR')}</p>
                </article>
              ))}
            </div>
          )}
        </section>

        <section aria-labelledby="motor-readings-title" className="space-y-3">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <h2 id="motor-readings-title" className="text-lg font-bold text-[var(--text-1)]">Sinais do motor</h2>
              <p className="mt-1 text-xs text-[var(--text-3)]">Até 120 leituras válidas mais recentes; os gráficos não preenchem lacunas.</p>
            </div>
            <span className="text-[10px] text-[var(--text-3)]">
              {lastReading ? `Última leitura válida: ${formatTime(lastReading.timestamp)}` : 'Nenhuma leitura válida'}
            </span>
          </div>
          {data.serie.length === 0 ? (
            <EmptyState title="Ainda não há leituras CAN válidas." message="Verifique a ingestão e a qualidade do pacote antes de interpretar os sinais como normais." />
          ) : (
            <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
              {metricSpecs.map((spec) => (
                <MetricChart key={spec.field} reading={data.serie} {...spec} />
              ))}
            </div>
          )}
        </section>

        <section className="grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Qualidade da telemetria CAN">
          <article className="metric-card">
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">Leituras recebidas</p>
            <p className="mt-2 text-2xl font-bold text-[var(--text-1)]">{data.qualidade.recebidas}</p>
          </article>
          <article className="metric-card">
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">Aceitas</p>
            <p className="mt-2 text-2xl font-bold text-[color:var(--status-normal)]">{data.qualidade.aceitas}</p>
          </article>
          <article className="metric-card">
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">Descartadas</p>
            <p className="mt-2 text-2xl font-bold text-[color:var(--status-atencao)]">{data.qualidade.descartadas}</p>
          </article>
          <article className="metric-card">
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">Índice de qualidade</p>
            <p className="mt-2 text-2xl font-bold text-[var(--text-1)]">{qualityPercent === null ? 'N/D' : `${qualityPercent}%`}</p>
          </article>
        </section>

        {(Object.keys(data.qualidade.motivos).length > 0
          || Object.keys(data.qualidade.campos_ausentes).length > 0
          || Object.keys(data.qualidade.sinais_congelados).length > 0) && (
          <section className="metric-card space-y-4" aria-label="Detalhamento da qualidade dos dados">
            <h2 className="text-sm font-bold text-[var(--text-1)]">Integridade dos sinais</h2>
            <CounterList title="Motivos de descarte" counts={data.qualidade.motivos} />
            <CounterList title="Campos ausentes (leituras parciais)" counts={data.qualidade.campos_ausentes} />
            <CounterList title="Sinais congelados" counts={data.qualidade.sinais_congelados} />
          </section>
        )}

        <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-[var(--line)] pt-4 text-[10px] text-[var(--text-3)]" role="status">
          <span>{refreshing ? 'Atualizando…' : 'Atualização automática a cada 5 segundos.'}{updatedAt ? ` Atualizado às ${updatedAt.toLocaleTimeString('pt-BR')}.` : ''}</span>
          <span>Última CAN: {lastReading ? formatTime(lastReading.timestamp) : 'sem leitura válida'}</span>
        </footer>
      </div>
    </AppShell>
  );
}

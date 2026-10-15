'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createPortal } from 'react-dom';
import {
  Search,
  UserPlus,
  Users,
  X,
  Briefcase,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { EmptyState } from '@/components/EmptyState';
import { OperatorFormModal } from '@/components/OperatorFormModal';
import { StatusBadge } from '@/components/StatusBadge';
import type { Operator } from '@/types/telemetry';

/* ──────────────────────────────────────────────────────────────────────────
   OperatorDirectory — a equipe de campo.

   Layout:
     · Barra de ação (busca + filtro + cadastro)
     · Faixa de KPIs compactos (3 tiles inline)
     · Corpo: lista densa à esquerda + painel de detalhe à direita (lg+)
       Abaixo de lg, detalhe abre como bottom-sheet (portal no body)

   Os KPIs usam o mesmo `.kpi-group` do dashboard de máquinas para manter
   consistência visual — mesma família, mesmo peso.
   ────────────────────────────────────────────────────────────────────────── */

type StatusFiltro = 'todos' | 'no-banco' | 'fora';

const FILTROS: { id: StatusFiltro; label: string }[] = [
  { id: 'todos', label: 'Todos' },
  { id: 'no-banco', label: 'Ativo' },
  { id: 'fora', label: 'Fora' },
];

function initialsOf(nome: string): string {
  const partes = nome.trim().split(/\s+/).filter(Boolean);
  if (!partes.length) return '—';
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return `${partes[0][0]}${partes[partes.length - 1][0]}`.toUpperCase();
}

function useIsWide(): boolean {
  const [largo, setLargo] = useState(true);
  useEffect(() => {
    const q = window.matchMedia('(min-width: 1024px)');
    const update = () => setLargo(q.matches);
    update();
    q.addEventListener('change', update);
    return () => q.removeEventListener('change', update);
  }, []);
  return largo;
}

/* ── Painel de detalhe do operário ─────────────────────────────────────── */
function OperatorDetail({
  operator,
  onClose,
}: {
  operator: Operator;
  onClose?: () => void;
}) {
  const statusOk = operator.no_banco;

  return (
    <section
      aria-label={`Detalhes de ${operator.nome}`}
      className="op-detail-card flex flex-col gap-5"
    >
      {/* Cabeçalho */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <span className="avatar-tile avatar-tile--lg" aria-hidden="true">
            {initialsOf(operator.nome)}
          </span>
          <div className="min-w-0">
            <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[color:var(--ui-accent)]">
              Operário
            </p>
            <h2 className="mt-0.5 truncate text-base font-bold text-[var(--text-1)]">
              {operator.nome}
            </h2>
          </div>
        </div>
        {onClose ? (
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[var(--panel-glass-mid)] text-[var(--text-3)] transition hover:text-[var(--text-1)] active:scale-95"
          >
            <X size={14} aria-hidden="true" />
          </button>
        ) : null}
      </div>

      {/* Status em destaque */}
      <div
        className={`op-status-banner ${statusOk ? 'op-status-banner--active' : 'op-status-banner--inactive'}`}
      >
        {statusOk ? (
          <CheckCircle2 size={15} aria-hidden="true" />
        ) : (
          <AlertCircle size={15} aria-hidden="true" />
        )}
        <span className="text-sm font-semibold">
          {statusOk ? 'Ativo no banco' : 'Fora de campo'}
        </span>
      </div>

      {/* Dados */}
      <dl className="grid grid-cols-2 gap-3">
        <div className="op-tile">
          <dt className="op-tile__label">Registro</dt>
          <dd className="op-tile__value font-mono">#{operator.id}</dd>
        </div>
        <div className="op-tile">
          <dt className="op-tile__label">Experiência</dt>
          <dd className="op-tile__value">
            {operator.tempo_de_servico}{' '}
            <span className="text-[var(--text-3)] font-normal text-sm">
              {operator.tempo_de_servico === 1 ? 'ano' : 'anos'}
            </span>
          </dd>
        </div>
      </dl>

      <p className="text-[11px] text-[var(--text-3)] leading-relaxed">
        Edição e inativação de operários ainda não têm tela — em desenvolvimento.
      </p>
    </section>
  );
}

/* ── Componente principal ──────────────────────────────────────────────── */
export function OperatorDirectory({ operators }: { operators: Operator[] }) {
  const router = useRouter();
  const [lista, setLista] = useState<Operator[]>(operators);
  const [busca, setBusca] = useState('');
  const [filtro, setFiltro] = useState<StatusFiltro>('todos');
  const [selecionadoId, setSelecionadoId] = useState<number | null>(null);
  const [formAberto, setFormAberto] = useState(false);
  const [montado, setMontado] = useState(false);
  const largo = useIsWide();

  useEffect(() => setMontado(true), []);
  useEffect(() => { setLista(operators); }, [operators]);

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase();
    return lista.filter((op) => {
      if (filtro === 'no-banco' && !op.no_banco) return false;
      if (filtro === 'fora' && op.no_banco) return false;
      if (!termo) return true;
      return [op.nome, String(op.id), String(op.tempo_de_servico)].some((v) =>
        v.toLocaleLowerCase().includes(termo),
      );
    });
  }, [lista, busca, filtro]);

  const selecionado = useMemo(() => {
    if (selecionadoId !== null) {
      const found = lista.find((op) => op.id === selecionadoId);
      if (found) return found;
    }
    return filtrados[0] ?? null;
  }, [lista, filtrados, selecionadoId]);

  const ativos = lista.filter((op) => op.no_banco).length;
  const inativos = lista.length - ativos;
  const tempoMedio =
    lista.length
      ? lista.reduce((s, op) => s + op.tempo_de_servico, 0) / lista.length
      : 0;

  function handleCreated(op: Operator) {
    setLista((prev) => [...prev, op]);
    setSelecionadoId(op.id);
    router.refresh();
  }

  return (
    <div className="space-y-5">

      {/* ── Barra de ação ─────────────────────────────────────────────── */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Busca */}
        <label className="relative block w-full sm:max-w-xs">
          <span className="sr-only">Buscar operários</span>
          <Search
            size={13}
            aria-hidden="true"
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-3)]"
          />
          <input
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar por nome ou registro"
            className="icon-control h-10 w-full rounded-xl border pl-8 pr-3 text-sm text-[var(--text-1)] outline-none placeholder:text-[var(--text-3)] focus:border-[color:var(--ui-accent)]/60"
          />
        </label>

        <div className="flex items-center gap-2">
          {/* Filtro */}
          <div
            role="group"
            aria-label="Filtrar por situação"
            className="flex items-center gap-0.5 rounded-xl border border-[var(--line)] bg-[var(--panel-glass-mid)] p-1"
          >
            {FILTROS.map(({ id, label }) => (
              <button
                key={id}
                type="button"
                onClick={() => setFiltro(id)}
                aria-pressed={filtro === id}
                className={`rounded-lg px-3 py-1.5 text-[11px] font-semibold transition-colors duration-150 focus-visible:outline focus-visible:outline-2 ${
                  filtro === id
                    ? 'bg-[var(--panel-glass-strong)] text-[var(--text-1)]'
                    : 'text-[var(--text-3)] hover:text-[var(--text-1)]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Cadastrar */}
          <button
            type="button"
            onClick={() => setFormAberto(true)}
            className="btn-brand inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
          >
            <UserPlus size={15} aria-hidden="true" />
            <span className="hidden sm:inline">Cadastrar</span>
            <span className="sr-only sm:hidden">Cadastrar operário</span>
          </button>
        </div>
      </div>

      {/* ── KPIs da equipe ────────────────────────────────────────────── */}
      <section aria-label="Resumo da equipe" className="kpi-group">
        <div className="kpi-group__head">
          <div>
            <p className="kpi-group__title">Equipe de campo</p>
            <p className="kpi-group__sub">{lista.length} operários cadastrados no sistema</p>
          </div>
        </div>
        <div className="kpi-group__grid">
          {/* Total */}
          <article className="metric-card flex items-center gap-4" aria-label="Total cadastrado">
            <span className="op-kpi-icon op-kpi-icon--accent">
              <Users size={17} aria-hidden="true" />
            </span>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">Cadastrados</p>
              <p className="stat-value text-3xl font-bold text-[var(--text-1)]">{lista.length}</p>
            </div>
          </article>
          {/* Ativos */}
          <article className="metric-card flex items-center gap-4" aria-label="Ativos no banco">
            <span className="op-kpi-icon op-kpi-icon--green">
              <CheckCircle2 size={17} aria-hidden="true" />
            </span>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">No banco</p>
              <p className="stat-value stat-value--normal text-3xl font-bold">{ativos}</p>
              <p className="text-[10px] text-[var(--text-3)]">{inativos} fora</p>
            </div>
          </article>
          {/* Experiência */}
          <article className="metric-card flex items-center gap-4" aria-label="Experiência média">
            <span className="op-kpi-icon op-kpi-icon--amber">
              <Briefcase size={17} aria-hidden="true" />
            </span>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">Experiência</p>
              <p className="stat-value stat-value--atencao text-3xl font-bold">
                {tempoMedio.toFixed(1)}
                <span className="ml-1 text-base font-normal text-[var(--text-3)]">anos</span>
              </p>
              <p className="text-[10px] text-[var(--text-3)]">média da equipe</p>
            </div>
          </article>
        </div>
      </section>

      {/* ── Lista + Detalhe ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)] lg:items-start">

        {/* Lista */}
        <section aria-label="Lista de operários">
          {filtrados.length === 0 ? (
            <EmptyState
              title={lista.length === 0 ? 'Nenhum operário cadastrado.' : 'Nenhum resultado.'}
              message={
                lista.length === 0
                  ? 'Use o botão Cadastrar para adicionar o primeiro operário.'
                  : 'Ajuste a busca ou o filtro para encontrar outro operário.'
              }
            />
          ) : (
            <div className="op-list-card">
              {/* Cabeçalho da tabela */}
              <div className="op-list-header">
                <span>Operário</span>
                <span className="text-right">Exp.</span>
                <span className="text-right">Status</span>
              </div>

              <ul className="divide-y divide-[var(--border-subtle)]">
                {filtrados.map((op) => {
                  const ativo = selecionado?.id === op.id;
                  return (
                    <li key={op.id}>
                      <button
                        type="button"
                        onClick={() => setSelecionadoId(op.id)}
                        aria-pressed={ativo}
                        className={`op-list-row ${ativo ? 'op-list-row--active' : ''}`}
                      >
                        {/* Avatar + nome */}
                        <span className="flex min-w-0 items-center gap-3">
                          <span className="avatar-tile shrink-0" aria-hidden="true">
                            {initialsOf(op.nome)}
                          </span>
                          <span className="min-w-0">
                            <span className="block truncate text-sm font-semibold text-[var(--text-1)]">
                              {op.nome}
                            </span>
                            <span className="block text-[11px] text-[var(--text-3)]">
                              #{op.id}
                            </span>
                          </span>
                        </span>

                        {/* Experiência */}
                        <span className="shrink-0 text-right text-sm font-medium tabular-nums text-[var(--text-2)]">
                          {op.tempo_de_servico}a
                        </span>

                        {/* Status */}
                        <span className="shrink-0 text-right">
                          <StatusBadge tone={op.no_banco ? 'normal' : 'warning'}>
                            {op.no_banco ? 'Ativo' : 'Fora'}
                          </StatusBadge>
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>

              <div className="px-4 py-2.5 text-[10px] text-[var(--text-3)]">
                {filtrados.length} de {lista.length} operário{lista.length !== 1 ? 's' : ''}
              </div>
            </div>
          )}
        </section>

        {/* Detalhe (desktop) */}
        {selecionado ? (
          <div className="hidden lg:block">
            <OperatorDetail operator={selecionado} />
          </div>
        ) : null}
      </div>

      {/* Detalhe mobile: bottom-sheet via portal */}
      {!largo && montado && selecionado
        ? createPortal(
            <div
              className="fixed inset-0 z-[110] flex items-end justify-center bg-black/70 p-3 backdrop-blur-sm sm:items-center"
              role="presentation"
              onMouseDown={(e) => { if (e.target === e.currentTarget) setSelecionadoId(null); }}
            >
              <div className="max-h-[85dvh] w-full max-w-[32rem] overflow-y-auto">
                <OperatorDetail operator={selecionado} onClose={() => setSelecionadoId(null)} />
              </div>
            </div>,
            document.body,
          )
        : null}

      <OperatorFormModal
        isOpen={formAberto}
        onClose={() => setFormAberto(false)}
        onCreated={handleCreated}
      />
    </div>
  );
}

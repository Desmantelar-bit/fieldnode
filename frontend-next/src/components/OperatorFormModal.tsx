'use client';

import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Loader2, UserPlus, X } from 'lucide-react';
import { createOperator, OperatorError } from '@/services/operatorService';
import type { Operator } from '@/types/telemetry';

/* ──────────────────────────────────────────────────────────────────────────
   OperatorFormModal — cadastro de operário.

   Grava de verdade: POST /api/operario/ (ver operatorService). Depois de criar,
   devolve o registro para a lista inserir na hora e pede ao Next para revalidar
   a página (`router.refresh` no consumidor), então o servidor e a tela voltam a
   contar a mesma história.

   Os três campos são exatamente os do modelo — nome, tempo de serviço e se está
   no banco. Nenhum campo inventado para "completar" o formulário.
   ────────────────────────────────────────────────────────────────────────── */

type OperatorFormModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (operator: Operator) => void;
};

export function OperatorFormModal({ isOpen, onClose, onCreated }: OperatorFormModalProps) {
  const [mounted, setMounted] = useState(false);
  const [nome, setNome] = useState('');
  const [tempo, setTempo] = useState('0');
  const [noBanco, setNoBanco] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const nomeRef = useRef<HTMLInputElement>(null);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!isOpen) return;
    const overflowAnterior = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    const foco = window.setTimeout(() => nomeRef.current?.focus(), 60);

    return () => {
      document.body.style.overflow = overflowAnterior;
      window.removeEventListener('keydown', onKeyDown);
      window.clearTimeout(foco);
    };
  }, [isOpen, onClose]);

  // Só monta no cliente: o modal vive num portal para o <body>.
  if (!mounted || !isOpen) return null;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (salvando) return;

    const nomeLimpo = nome.trim();
    if (!nomeLimpo) {
      setErro('Informe o nome do operário.');
      nomeRef.current?.focus();
      return;
    }

    setSalvando(true);
    setErro(null);

    try {
      const criado = await createOperator({
        nome: nomeLimpo,
        tempo_de_servico: Number(tempo) || 0,
        no_banco: noBanco,
      });
      onCreated(criado);
      setNome('');
      setTempo('0');
      setNoBanco(true);
      onClose();
    } catch (err) {
      setErro(
        err instanceof OperatorError
          ? err.message
          : 'Não foi possível cadastrar o operário agora.',
      );
    } finally {
      setSalvando(false);
    }
  }

  return createPortal(
    <div
      className="fixed inset-0 z-[120] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="operator-form-title"
        className="liquid-glass--elevated w-full max-w-md p-6 shadow-[var(--shadow-elevated)]"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--panel-glass-strong)] text-[color:var(--ui-accent)]" aria-hidden="true">
              <UserPlus size={19} />
            </span>
            <div>
              <p className="section-heading">Equipe</p>
              <h2 id="operator-form-title" className="mt-0.5 text-lg font-bold text-[var(--text-1)]">
                Cadastrar operário
              </h2>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar cadastro"
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--panel-glass-mid)] text-[var(--text-3)] transition hover:text-[var(--text-1)] focus-visible:outline-2 active:scale-95"
          >
            <X size={15} aria-hidden="true" />
          </button>
        </div>

        <form onSubmit={handleSubmit} noValidate className="mt-5 flex flex-col gap-4">
          {erro ? (
            <p className="auth-error-block" role="alert">{erro}</p>
          ) : null}

          <div className="auth-field auth-field--pill">
            <label htmlFor="fn-op-nome">
              Nome <span className="text-[color:var(--status-critico)]">*</span>
            </label>
            <input
              ref={nomeRef}
              id="fn-op-nome"
              type="text"
              value={nome}
              onChange={(event) => {
                setNome(event.target.value);
                setErro(null);
              }}
              disabled={salvando}
              aria-required="true"
              className="auth-input"
              placeholder="Nome completo"
              maxLength={100}
            />
          </div>

          <div className="auth-field auth-field--pill">
            <label htmlFor="fn-op-tempo">Tempo de serviço (anos)</label>
            <input
              id="fn-op-tempo"
              type="number"
              min={0}
              step={1}
              inputMode="numeric"
              value={tempo}
              onChange={(event) => setTempo(event.target.value)}
              disabled={salvando}
              className="auth-input"
            />
          </div>

          <div className="data-tile flex items-center justify-between gap-4 p-3">
            <div className="min-w-0">
              <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--text-3)]">
                No banco
              </p>
              <p className="mt-0.5 text-xs text-[var(--text-3)]">
                Indica se a pessoa está em atividade agora.
              </p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={noBanco}
              onClick={() => setNoBanco((valor) => !valor)}
              disabled={salvando}
              className={`relative h-6 w-11 shrink-0 rounded-full border transition-colors duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
                noBanco
                  ? 'border-transparent bg-[color:var(--status-normal)]'
                  : 'border-[var(--line)] bg-[var(--panel-glass-strong)]'
              }`}
            >
              <span className="sr-only">{noBanco ? 'No banco' : 'Fora do banco'}</span>
              <span
                aria-hidden="true"
                className={`absolute top-1/2 h-4 w-4 -translate-y-1/2 rounded-full bg-white shadow transition-all duration-200 ${
                  noBanco ? 'left-[1.5rem]' : 'left-1'
                }`}
              />
            </button>
          </div>

          <div className="mt-1 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={salvando}
              className="rounded-xl border border-[var(--line)] px-4 py-2.5 text-sm font-semibold text-[var(--text-2)] transition hover:bg-[var(--panel-glass-mid)] hover:text-[var(--text-1)] active:scale-[0.98] disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={salvando}
              aria-busy={salvando}
              className="btn-brand inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              {salvando ? (
                <>
                  <Loader2 size={16} className="animate-spin" aria-hidden="true" /> Cadastrando…
                </>
              ) : (
                <>
                  <UserPlus size={16} aria-hidden="true" /> Cadastrar
                </>
              )}
            </button>
          </div>
        </form>
      </section>
    </div>,
    document.body,
  );
}

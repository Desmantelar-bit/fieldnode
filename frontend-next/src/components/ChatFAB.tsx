'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { ChevronDown, Sparkles, Tractor, WifiOff, X } from 'lucide-react';
import { PrescricaoModal } from '@/components/PrescricaoModal';

type ChatMachine = {
  maquina_id?: string | null;
  modelo?: { nome?: string };
};

type ChatFABProps = {
  machines: ChatMachine[];
};

const PANEL_ID = 'pergunte-a-ia-painel';

/** Quantas máquinas viram sugestão rápida — o restante continua no <select>. */
const MAX_SUGESTOES = 3;

export function ChatFAB({ machines }: ChatFABProps) {
  const machineOptions = useMemo(
    () => machines.filter((m): m is ChatMachine & { maquina_id: string } => Boolean(m.maquina_id)),
    [machines],
  );

  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);
  const [offline, setOffline] = useState(false);
  const [selectedMachine, setSelectedMachine] = useState(machineOptions[0]?.maquina_id ?? '');
  const [showPrescription, setShowPrescription] = useState(false);

  const fabRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLElement>(null);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!machineOptions.some((machine) => machine.maquina_id === selectedMachine)) {
      setSelectedMachine(machineOptions[0]?.maquina_id ?? '');
    }
  }, [machineOptions, selectedMachine]);

  // Estado offline real do navegador — nada de simular falha de integração.
  useEffect(() => {
    const sync = () => setOffline(!window.navigator.onLine);
    sync();
    window.addEventListener('online', sync);
    window.addEventListener('offline', sync);
    return () => {
      window.removeEventListener('online', sync);
      window.removeEventListener('offline', sync);
    };
  }, []);

  const fechar = useCallback(() => {
    setOpen(false);
    fabRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!open) return;
    panelRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') fechar();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open, fechar]);

  const analisar = useCallback((machineId: string) => {
    if (!machineId) return;
    setSelectedMachine(machineId);
    setShowPrescription(true);
  }, []);

  const sugestoes = useMemo(() => machineOptions.slice(0, MAX_SUGESTOES), [machineOptions]);
  const semFrota = machineOptions.length === 0;

  // Indicador de estado: reflete a conectividade real e a disponibilidade da frota.
  const estado = offline
    ? { rotulo: 'Offline', cor: 'var(--status-atencao)', halo: 'var(--glow-amber)' }
    : semFrota
      ? { rotulo: 'Sem frota', cor: 'var(--text-3)', halo: 'transparent' }
      : { rotulo: 'Conectado', cor: 'var(--status-normal)', halo: 'var(--glow-normal-strong)' };

  if (!mounted) return null;

  return createPortal(
    <>
      {open && (
        /* O slot externo é o único dono do `position: fixed`. O painel em si fica
           livre para usar a camada de vidro sem disputar com o utilitário —
           o CSS de globals.css é não-layerizado e venceria `.fixed`. */
        <div className="chat-panel-slot fixed z-[80]">
          <section
            ref={panelRef}
            id={PANEL_ID}
            tabIndex={-1}
            aria-label="Pergunte à IA"
            role="dialog"
            aria-modal="false"
            aria-describedby={`${PANEL_ID}-descricao`}
            className="chat-panel liquid-glass--elevated flex flex-col overflow-hidden outline-none"
          >
          {/* ── Header ─────────────────────────────────────────────── */}
            <header className="flex shrink-0 items-start justify-between gap-3 border-b border-[var(--border-subtle)] px-4 pb-3 pt-4 sm:px-5 sm:pt-5">
              <div className="flex min-w-0 gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[color:var(--ui-accent)]/14 text-[color:var(--ui-accent)] shadow-[0_0_20px_var(--glow-accent)]">
                  <Sparkles size={16} aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[color:var(--ui-accent)]">
                    Pergunte à IA
                  </p>
                  <h2 className="mt-0.5 truncate text-sm font-bold text-[var(--text-1)]">
                    O que merece atenção?
                  </h2>
                  <p
                    className="mt-1 inline-flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.1em]"
                    style={{ color: estado.cor }}
                    aria-live="polite"
                  >
                    <span
                      aria-hidden="true"
                      className="h-1.5 w-1.5 rounded-full"
                      style={{ backgroundColor: estado.cor, boxShadow: `0 0 6px ${estado.halo}` }}
                    />
                    {estado.rotulo}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={fechar}
                aria-label="Fechar assistente"
                title="Fechar assistente"
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[var(--panel-glass-mid)] text-[var(--text-3)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] active:scale-95"
              >
                <X size={14} aria-hidden="true" />
              </button>
            </header>

            {/* ── Corpo rolável ──────────────────────────────────────── */}
            <div className="chat-scroll min-h-0 flex-1 px-4 py-4 sm:px-5">
              <p
                id={`${PANEL_ID}-descricao`}
                className="chat-bubble p-3 text-xs leading-relaxed text-[var(--text-2)]"
              >
                Selecione uma máquina para consultar a prescrição operacional gerada a partir da
                telemetria disponível.
              </p>

              {offline && (
                <p className="mt-3 flex items-start gap-2 rounded-xl bg-[color:var(--status-atencao)]/10 p-2.5 text-[11px] leading-relaxed text-[color:var(--status-atencao)]">
                  <WifiOff size={13} className="mt-0.5 shrink-0" aria-hidden="true" />
                  <span>Sem conexão com o servidor agora. A análise pode não responder.</span>
                </p>
              )}

              {semFrota ? (
                <p className="mt-3 rounded-xl bg-[var(--panel-glass-mid)] p-3 text-xs leading-relaxed text-[var(--text-2)]">
                  A frota ainda não está disponível. A assistente continuará visível e poderá ser
                  usada quando uma máquina for carregada.
                </p>
              ) : (
                <>
                  <label className="mt-4 grid gap-1.5">
                    <span className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
                      <Tractor size={11} aria-hidden="true" /> Máquina
                    </span>
                    <span className="relative">
                      <select
                        value={selectedMachine}
                        onChange={(e) => setSelectedMachine(e.target.value)}
                        aria-label="Escolher máquina para análise"
                        className="min-h-10 w-full appearance-none rounded-xl bg-[var(--panel-glass-mid)] px-3 pr-8 text-sm font-medium text-[var(--text-1)] outline-none transition hover:bg-[var(--panel-glass-strong)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)]"
                      >
                        {machineOptions.map((m) => (
                          <option key={m.maquina_id} value={m.maquina_id}>
                            {m.maquina_id}{m.modelo?.nome ? ` · ${m.modelo.nome}` : ''}
                          </option>
                        ))}
                      </select>
                      <ChevronDown
                        size={13}
                        className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-3)]"
                        aria-hidden="true"
                      />
                    </span>
                  </label>

                  {sugestoes.length > 0 && (
                    <div className="mt-4">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-3)]">
                        Sugestões rápidas
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {sugestoes.map((m) => (
                          <button
                            key={m.maquina_id}
                            type="button"
                            onClick={() => analisar(m.maquina_id)}
                            title={`Analisar ${m.maquina_id}`}
                            className="chat-chip inline-flex min-h-8 max-w-full items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-left text-[11px] font-semibold text-[var(--text-2)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)]"
                          >
                            <Sparkles size={11} aria-hidden="true" />
                            <span className="truncate">
                              {m.maquina_id}
                              {m.modelo?.nome ? ` · ${m.modelo.nome}` : ''}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* ── Rodapé fixo: nunca some sob rolagem ─────────────────── */}
            <footer className="chat-footer shrink-0 px-4 py-3 sm:px-5">
              <p className="mb-2 text-[10px] leading-relaxed text-[var(--text-3)]">
                A resposta vem da prescrição operacional do servidor — não é leitura ao vivo da
                telemetria.
              </p>
              <button
                type="button"
                onClick={() => analisar(selectedMachine)}
                disabled={!selectedMachine}
                className="btn-brand inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-xl px-4 text-sm font-bold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] disabled:cursor-not-allowed"
              >
                <Sparkles size={15} aria-hidden="true" />
                Analisar máquina
              </button>
            </footer>
          </section>
        </div>
      )}

      {/* Slot do botão: acima do mapa, do header e do conteúdo; abaixo do painel
          (z-80) e dos modais (z-120). */}
      <div className="chat-fab-slot fixed z-[70]">
        <button
          ref={fabRef}
          type="button"
          onClick={() => (open ? fechar() : setOpen(true))}
          aria-expanded={open}
          aria-controls={PANEL_ID}
          aria-label={open ? 'Fechar Pergunte à IA' : 'Abrir Pergunte à IA'}
          title={open ? 'Fechar Pergunte à IA' : 'Abrir Pergunte à IA'}
          className="chat-fab inline-flex h-11 w-11 items-center justify-center gap-2 rounded-full text-sm font-bold transition duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--ui-accent)] active:scale-[0.97] sm:w-auto sm:justify-start sm:px-4"
        >
          <Sparkles size={16} aria-hidden="true" />
          <span className="hidden sm:inline">Pergunte à IA</span>
        </button>
      </div>

      <PrescricaoModal
        machineId={selectedMachine}
        isOpen={showPrescription}
        onClose={() => setShowPrescription(false)}
      />
    </>,
    document.body,
  );
}

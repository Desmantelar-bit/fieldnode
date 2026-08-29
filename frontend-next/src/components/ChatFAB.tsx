'use client';

import { useState } from 'react';
import { ChevronDown, Sparkles, Tractor, X } from 'lucide-react';
import { PrescricaoModal } from '@/components/PrescricaoModal';
import { glassCard } from '@/lib/design-tokens';

type ChatMachine = {
  maquina_id?: string | null;
  modelo?: { nome?: string };
};

type ChatFABProps = {
  machines: ChatMachine[];
};

export function ChatFAB({ machines }: ChatFABProps) {
  const machineOptions = machines.filter((machine): machine is ChatMachine & { maquina_id: string } => Boolean(machine.maquina_id));
  const [open, setOpen] = useState(false);
  const [selectedMachine, setSelectedMachine] = useState(machineOptions[0]?.maquina_id ?? '');
  const [showPrescription, setShowPrescription] = useState(false);

  if (machineOptions.length === 0) return null;

  return (
    <>
      {open && (
        <section className={`fixed bottom-24 right-4 z-50 w-[calc(100vw-2rem)] max-w-sm p-5 shadow-2xl sm:right-6 lg:bottom-6 ${glassCard}`} aria-label="Assistente de campo">
          <div className="flex items-start justify-between gap-4">
            <div className="flex gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-accent/10 text-accent"><Sparkles aria-hidden="true" size={18} /></div>
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-accent">assistente de campo</p>
                <h2 className="mt-1 text-sm font-semibold text-field-text1">o que merece atenção?</h2>
              </div>
            </div>
            <button type="button" onClick={() => setOpen(false)} aria-label="Fechar assistente" className="rounded-full p-2 text-field-text3 transition hover:bg-white/10 hover:text-field-text1 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent active:scale-[0.97]"><X aria-hidden="true" size={16} /></button>
          </div>
          <p className="mt-4 text-xs leading-relaxed text-field-text3">Selecione uma máquina para consultar a prescrição operacional gerada a partir da telemetria disponível.</p>
          <label className="mt-4 grid gap-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-field-text3">
            máquina
            <span className="relative">
              <Tractor aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-field-text3" size={15} />
              <select value={selectedMachine} onChange={(event) => setSelectedMachine(event.target.value)} className="min-h-11 w-full appearance-none rounded-xl border border-white/10 bg-white/[0.06] pl-10 pr-9 text-sm font-medium normal-case tracking-normal text-field-text1 outline-none transition hover:border-white/20 focus:border-accent/60">
                {machineOptions.map((machine) => <option key={machine.maquina_id} value={machine.maquina_id} className="bg-slate-950 text-white">{machine.maquina_id}{machine.modelo?.nome ? ` · ${machine.modelo.nome}` : ''}</option>)}
              </select>
              <ChevronDown aria-hidden="true" className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-field-text3" size={15} />
            </span>
          </label>
          <button type="button" onClick={() => setShowPrescription(true)} disabled={!selectedMachine} className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-accent px-4 text-sm font-bold text-slate-950 transition hover:brightness-105 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-50 active:scale-[0.98]">
            <Sparkles aria-hidden="true" size={16} /> analisar máquina
          </button>
        </section>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="fixed bottom-24 right-4 z-40 inline-flex min-h-12 items-center gap-2 rounded-full bg-accent px-5 text-sm font-bold text-slate-950 shadow-[0_0_28px_var(--glow-normal)] transition hover:brightness-105 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent active:scale-[0.97] sm:right-6 lg:bottom-6"
      >
        <Sparkles aria-hidden="true" size={17} />
        <span className="hidden sm:inline">perguntar à IA</span>
        <span className="sm:hidden">assistente</span>
      </button>

      <PrescricaoModal machineId={selectedMachine} isOpen={showPrescription} onClose={() => setShowPrescription(false)} />
    </>
  );
}

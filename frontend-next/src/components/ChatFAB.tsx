'use client';

import { useState } from 'react';
import { Bot, Send, Sparkles, X } from 'lucide-react';
import { glassCard } from '@/lib/design-tokens';

export function ChatFAB() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [submitted, setSubmitted] = useState(false);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) return;
    setSubmitted(true);
    setQuestion('');
  }

  return (
    <>
      {open ? (
        <section aria-label="Assistente FieldNode" className={`fixed bottom-24 right-4 z-[60] flex h-[min(32rem,calc(100vh-8rem))] w-[min(24rem,calc(100vw-2rem))] flex-col overflow-hidden ${glassCard}`}>
          <header className="flex items-center justify-between border-b border-white/10 px-5 py-4">
            <div className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-accent/15 text-accent"><Bot size={18} /></span><div><p className="text-sm font-semibold text-white">fieldnode copilot</p><p className="text-xs text-slate-400">insights da sua operação</p></div></div>
            <button type="button" aria-label="Fechar assistente" onClick={() => setOpen(false)} className="rounded-full p-2 text-slate-400 hover:bg-white/10 hover:text-white"><X size={18} /></button>
          </header>
          <div className="flex-1 space-y-3 overflow-y-auto p-5 text-sm">
            <div className="max-w-[90%] rounded-2xl rounded-tl-sm bg-white/5 px-4 py-3 text-slate-200">olá. posso ajudar a interpretar a telemetria da frota.</div>
            {submitted ? <div className="ml-auto max-w-[90%] rounded-2xl rounded-tr-sm bg-accent px-4 py-3 text-slate-950">pergunta recebida. conecte o endpoint de prescrições para obter a explicação operacional.</div> : null}
          </div>
          <form onSubmit={submit} className="flex gap-2 border-t border-white/10 p-4"><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="pergunte sobre a frota..." className="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/20 px-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-accent" /><button type="submit" aria-label="Enviar pergunta" className="rounded-xl bg-accent px-3 text-slate-950 transition-transform active:scale-95"><Send size={17} /></button></form>
        </section>
      ) : null}
      <button type="button" aria-expanded={open} onClick={() => setOpen((value) => !value)} className="fixed bottom-24 right-4 z-50 inline-flex items-center gap-2 rounded-full bg-accent px-4 py-3 text-sm font-semibold text-slate-950 shadow-[0_0_24px_rgba(204,255,0,0.22)] transition-transform hover:-translate-y-0.5 active:scale-95 lg:bottom-6"><Sparkles size={17} /> perguntar à ia</button>
    </>
  );
}

"use client";

import Image from "next/image";
import { createPortal } from "react-dom";
import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, X } from "lucide-react";
import { team } from "@/data/team";

export function TeamPanel() {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const panelRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!open) return;
    const panel = panelRef.current;
    if (!panel) return;
    const trigger = triggerRef.current;
    const focusables = () => Array.from(panel.querySelectorAll<HTMLElement>(
      'button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])',
    ));
    focusables()[0]?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
      if (event.key !== "Tab") return;
      const items = focusables();
      if (!items.length) return;
      if (event.shiftKey && document.activeElement === items[0]) {
        event.preventDefault(); items[items.length - 1].focus();
      } else if (!event.shiftKey && document.activeElement === items[items.length - 1]) {
        event.preventDefault(); items[0].focus();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      trigger?.focus();
    };
  }, [open]);

  return (
    <>
      <button type="button" onClick={(event) => { triggerRef.current = event.currentTarget; setOpen(true); }} aria-haspopup="dialog" aria-expanded={open} className="hidden min-h-10 items-center gap-2 rounded-xl border border-[var(--line)] px-3 text-xs font-semibold text-[var(--text-2)] transition hover:border-[var(--border-highlight)] hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[color:var(--ui-accent)] sm:inline-flex">
        <span className="flex -space-x-1.5" aria-hidden="true">{team.slice(0, 3).map((member) => <Image key={member.id} src={member.photo} alt="" width={22} height={22} className="h-[22px] w-[22px] rounded-full border-2 border-[var(--surface-1)] object-cover" />)}</span>
        Por trás do FieldNode
      </button>
      <button type="button" onClick={(event) => { triggerRef.current = event.currentTarget; setOpen(true); }} aria-label="Conheça quem faz o FieldNode" aria-haspopup="dialog" aria-expanded={open} className="flex h-10 w-10 items-center justify-center rounded-xl border border-[var(--line)] text-[var(--text-2)] transition hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[color:var(--ui-accent)] sm:hidden">
        <span className="flex -space-x-2" aria-hidden="true">{team.slice(0, 3).map((member) => <Image key={member.id} src={member.photo} alt="" width={22} height={22} className="h-[22px] w-[22px] rounded-full border-2 border-[var(--surface-1)] object-cover" />)}</span>
      </button>
      {open && typeof document !== "undefined" ? createPortal(
        <div className="team-panel-backdrop fixed inset-0 z-[100] flex items-end justify-center bg-black/65 p-0 backdrop-blur-sm sm:items-center sm:p-6" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
          <section ref={panelRef} role="dialog" aria-modal="true" aria-labelledby="team-panel-title" className="team-panel w-full max-w-5xl overflow-y-auto rounded-t-[1.75rem] border border-[var(--line)] bg-[var(--surface-1)] p-5 shadow-2xl sm:max-h-[min(90vh,900px)] sm:rounded-[1.75rem] sm:p-8">
            <div className="flex items-start justify-between gap-4 border-b border-[var(--line)] pb-5 sm:pb-7">
              <div><p className="section-heading">FieldNode · construção coletiva</p><h2 id="team-panel-title" className="mt-2 max-w-2xl text-2xl font-semibold leading-tight tracking-tight text-[var(--text-1)] sm:text-4xl">Quem está por trás do FieldNode</h2><p className="mt-2 max-w-xl text-sm leading-relaxed text-[var(--text-3)]">Quatro frentes conectadas para aproximar máquinas, dados e decisões.</p></div>
              <button type="button" onClick={() => setOpen(false)} aria-label="Fechar painel da equipe" className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-[var(--line)] text-[var(--text-1)] transition hover:bg-[var(--panel-glass-strong)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[color:var(--ui-accent)]"><X size={18} aria-hidden="true" /></button>
            </div>
            <div className="grid grid-cols-1 gap-x-7 sm:grid-cols-2 sm:gap-y-0">
              {team.map((member, index) => (
                <article key={member.id} className="team-member-row group grid grid-cols-[5.25rem_1fr] gap-4 border-b border-[var(--line)] py-5 sm:grid-cols-[6.5rem_1fr] sm:py-6">
                  <div className="relative aspect-[4/5] overflow-hidden rounded-xl bg-[var(--surface-3)]"><Image src={member.photo} alt={`Fotografia de ${member.name}`} fill sizes="(max-width: 640px) 84px, 104px" className="object-cover transition duration-500 group-hover:scale-[1.04]" priority={index < 2} /></div>
                  <div className="flex min-w-0 flex-col justify-center">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--ui-accent)]">0{index + 1} · {member.contribution}</p>
                    <h3 className="mt-1 text-lg font-semibold tracking-tight text-[var(--text-1)] sm:text-xl">{member.name}</h3>
                    <p className="mt-1 max-w-sm text-xs leading-relaxed text-[var(--text-3)] sm:text-sm">{member.description}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <a href={member.linkedin} target="_blank" rel="noopener noreferrer" aria-label={`LinkedIn de ${member.name} (abre em nova aba)`} className="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-[var(--line)] px-2.5 text-xs font-medium text-[var(--text-2)] transition hover:border-[var(--ui-accent)]/50 hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[color:var(--ui-accent)]">LinkedIn <ArrowUpRight size={12} aria-hidden="true" /></a>
                      {member.github ? <a href={member.github} target="_blank" rel="noopener noreferrer" aria-label={`GitHub de ${member.name} (abre em nova aba)`} className="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-[var(--line)] px-2.5 text-xs font-medium text-[var(--text-2)] transition hover:border-[var(--ui-accent)]/50 hover:text-[var(--text-1)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[color:var(--ui-accent)]">GitHub <ArrowUpRight size={12} aria-hidden="true" /></a> : null}
                    </div>
                  </div>
                </article>
              ))}
            </div>
            <p className="pt-4 text-[10px] text-[var(--text-3)]">As áreas descrevem a contribuição de cada integrante no projeto.</p>
          </section>
        </div>, document.body,
      ) : null}
    </>
  );
}

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <section className="glass-panel rounded-lg border-dashed p-8 text-center">
      <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500">Sem dados</p>
      <h2 className="mt-2 text-lg font-semibold text-slate-100">{title}</h2>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-400">{message}</p>
    </section>
  );
}

export function ErrorState({ title, message }: { title: string; message: string }) {
  return (
    <section className="rounded-lg border border-red-300/20 bg-red-300/10 p-6">
      <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-red-200">Falha ao carregar</p>
      <h2 className="mt-2 text-lg font-semibold text-slate-100">{title}</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-red-100/75">{message}</p>
    </section>
  );
}

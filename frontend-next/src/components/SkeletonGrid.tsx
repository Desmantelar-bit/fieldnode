export function SkeletonGrid() {
  return (
    <div
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      aria-label="Carregando dados da frota"
      aria-busy="true"
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="metric-card animate-pulse">
          <div className="flex items-start justify-between gap-3">
            <div className="space-y-2">
              <div className="h-2.5 w-16 rounded-full bg-[var(--panel-glass-strong)]" />
              <div className="h-4 w-24 rounded-lg bg-[var(--panel-glass-strong)]" />
            </div>
            <div className="h-6 w-16 rounded-full bg-[var(--panel-glass-strong)]" />
          </div>
          <div className="mt-5 grid grid-cols-3 gap-2">
            {[1, 2, 3].map((j) => (
              <div key={j} className="h-14 rounded-xl bg-[var(--panel-glass-mid)]" />
            ))}
          </div>
          <div className="mt-4 h-9 rounded-xl bg-[var(--panel-glass-mid)]" />
        </div>
      ))}
    </div>
  );
}

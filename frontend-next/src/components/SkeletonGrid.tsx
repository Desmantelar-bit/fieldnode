export function SkeletonGrid() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-label="Carregando dados da frota">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="glass-panel animate-pulse rounded-3xl p-5">
          <div className="h-3 w-24 rounded-full bg-white/10" />
          <div className="mt-4 h-9 w-28 rounded-2xl bg-white/10" />
          <div className="mt-6 h-2 w-full rounded-full bg-white/10" />
          <div className="mt-6 h-3 w-40 rounded-full bg-white/10" />
        </div>
      ))}
    </div>
  );
}

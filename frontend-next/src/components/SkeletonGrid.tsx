export function SkeletonGrid() {
  return (
    <div className="animate-pulse grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="h-40 bg-slate-100 rounded-xl border border-slate-200" />
      ))}
    </div>
  );
}
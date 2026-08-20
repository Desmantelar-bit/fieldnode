export function SkeletonGrid() {
  return (
    <div className="grid animate-pulse grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="h-52 rounded-lg border border-white/10 bg-white/[0.035] p-4">
          <div className="h-5 w-2/3 rounded bg-white/10" />
          <div className="mt-3 h-4 w-1/2 rounded bg-white/5" />
          <div className="mt-8 grid grid-cols-2 gap-3">
            <div className="h-16 rounded-md bg-white/5" />
            <div className="h-16 rounded-md bg-white/5" />
            <div className="h-16 rounded-md bg-white/5" />
            <div className="h-16 rounded-md bg-white/5" />
          </div>
        </div>
      ))}
    </div>
  );
}

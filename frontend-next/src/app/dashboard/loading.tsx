import { SkeletonGrid } from '@/components/SkeletonGrid';

export default function DashboardLoading() {
  return (
    <main
      className="min-h-screen bg-[var(--surface-page)] px-4 py-6 lg:ml-[5.5rem] lg:pr-8"
      aria-label="Carregando dashboard"
    >
      <div className="mx-auto max-w-7xl">
        <div className="flex items-center justify-between gap-4 pb-5">
          <div className="space-y-2">
            <div className="h-2.5 w-16 animate-pulse rounded-full bg-[var(--panel-glass-strong)]" />
            <div className="h-6 w-56 animate-pulse rounded-xl bg-[var(--panel-glass-strong)]" />
          </div>
          <div className="hidden h-9 w-32 animate-pulse rounded-xl bg-[var(--panel-glass-strong)] sm:block" />
        </div>
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="metric-card animate-pulse">
              <div className="h-2.5 w-20 rounded-full bg-[var(--panel-glass-strong)]" />
              <div className="mt-4 h-9 w-28 rounded-xl bg-[var(--panel-glass-strong)]" />
              <div className="mt-4 h-10 rounded-xl bg-[var(--panel-glass-mid)]" />
            </div>
          ))}
        </div>
        <div className="mt-6">
          <SkeletonGrid />
        </div>
      </div>
    </main>
  );
}

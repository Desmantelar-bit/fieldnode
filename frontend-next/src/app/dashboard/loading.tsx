import { SkeletonGrid } from '@/components/SkeletonGrid';

export default function DashboardLoading() {
  return (
    <main className="min-h-screen bg-[image:var(--surface-page)] px-4 py-6 lg:pl-36 lg:pr-8" aria-label="Carregando dashboard">
      <div className="mx-auto max-w-7xl">
        <div className="flex items-center justify-between gap-4 border-b border-field-border pb-5">
          <div className="space-y-3">
            <div className="h-3 w-20 animate-pulse rounded-full bg-white/10" />
            <div className="h-8 w-64 animate-pulse rounded-2xl bg-white/10" />
          </div>
          <div className="hidden h-11 w-36 animate-pulse rounded-full bg-white/10 sm:block" />
        </div>
        <div className="mt-8"><SkeletonGrid /></div>
      </div>
    </main>
  );
}

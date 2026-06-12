import { SkeletonGrid } from '@/components/SkeletonGrid';

export default function DashboardLoading() {
  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 sm:mb-8">
          <div className="h-8 w-56 animate-pulse rounded bg-slate-200" />
          <div className="mt-3 h-4 w-full max-w-md animate-pulse rounded bg-slate-200" />
        </header>
        <SkeletonGrid />
      </div>
    </main>
  );
}

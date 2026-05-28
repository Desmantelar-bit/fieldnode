import { Suspense } from 'react';
import { telemetryService } from '@/services/telemetryService';
import { FleetGrid } from '@/components/FleetGrid';
import { SkeletonGrid } from '@/components/SkeletonGrid';

async function FleetData() {
  // Server Component buscando dados diretamente
  const machines = await telemetryService.getFleetStatus();
  return <FleetGrid machines={machines} />;
}

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Frota FieldNode</h1>
          <p className="text-slate-500">Monitoramento em tempo real das colheitadeiras</p>
        </header>

        <Suspense fallback={<SkeletonGrid />}>
          <FleetData />
        </Suspense>
      </div>
    </main>
  );
}
import { Suspense } from 'react';
import { telemetryService } from '@/services/telemetryService';
import { FleetGrid } from '@/components/FleetGrid';
import { SkeletonGrid } from '@/components/SkeletonGrid';

async function FleetData() {
  let machines;

  try {
    machines = await telemetryService.getFleetStatus();
  } catch {
    return (
      <section className="rounded-lg border border-red-200 bg-white p-5 shadow-sm sm:p-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-red-600">Falha ao carregar</p>
        <h2 className="mt-2 text-xl font-bold text-slate-950">Nao consegui falar com a API agora.</h2>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
          Confira se o backend Django esta rodando em 127.0.0.1:8000. O dashboard continua de pe, so esta sem dados
          frescos para mostrar.
        </p>
      </section>
    );
  }

  return <FleetGrid machines={machines} />;
}

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">FieldNode</p>
            <h1 className="mt-1 text-2xl font-bold text-slate-950 sm:text-3xl">Frota em campo</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Monitoramento das colheitadeiras com cache offline e reenvio automatico de telemetria.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
            <span className="font-semibold text-slate-950">Sync offline</span>
            <span className="ml-2 text-emerald-700">ativo</span>
          </div>
        </header>

        <Suspense fallback={<SkeletonGrid />}>
          <FleetData />
        </Suspense>
      </div>
    </main>
  );
}

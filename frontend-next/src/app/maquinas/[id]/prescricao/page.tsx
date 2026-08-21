import { AppShell } from '@/components/AppShell';
import { ErrorState, EmptyState } from '@/components/EmptyState';
import { AnalisePrescricaoSchema } from '@/schemas';
import { resolveApiUrl } from '@/services/telemetryService';

function sourceLabel(source: string) {
  if (source === 'ia_generativa') return 'Explicação gerada por IA';
  if (source === 'fallback_determinístico') return 'Modo offline: recomendação segura';
  return 'Recomendação determinística';
}

export default async function PrescricaoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: maquinaId } = await params;

  if (!maquinaId) {
    return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
        <EmptyState title="Selecione uma máquina." message="Selecione uma máquina para ver a prescrição." />
      </AppShell>
    );
  }

  try {
    const response = await fetch(
      `${resolveApiUrl()}/prescricoes/${encodeURIComponent(maquinaId)}/`,
      { cache: 'no-store', headers: { Accept: 'application/json' } },
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const parsed = AnalisePrescricaoSchema.safeParse(await response.json());
    if (!parsed.success) throw new Error('Resposta da análise em formato inesperado.');
    const analise = parsed.data;
    const texto = analise.explicacao_operador || analise.recomendacao_tecnica || 'Nenhuma ação necessária.';

    return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
        <div className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-50">Prescrição para {maquinaId}</h1>
              <p className="mt-1 text-sm text-slate-400">Recomendação operacional baseada na telemetria atual.</p>
            </div>
            <a href="/colheitadeiras" className="rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]">
              Voltar
            </a>
          </div>

          <section className="glass-panel rounded-lg border border-white/10 bg-white/[0.02] p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-sm font-semibold text-slate-100">Status: {analise.status}</span>
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-200">
                {sourceLabel(analise.fonte_explicacao)}
              </span>
            </div>
            <p className="mt-4 text-base font-medium leading-relaxed text-slate-100">{texto}</p>
            {analise.recomendacao_tecnica && (
              <p className="mt-3 text-sm text-slate-300">Conduta técnica: {analise.recomendacao_tecnica}</p>
            )}
            {analise.motivos.length > 0 && (
              <p className="mt-3 text-sm text-slate-400">Motivos: {analise.motivos.join('; ')}.</p>
            )}
          </section>
        </div>
      </AppShell>
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Erro desconhecido';
    return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrição">
        <ErrorState title="Não consegui carregar a prescrição." message={`${message} — tente novamente.`} />
      </AppShell>
    );
  }
}

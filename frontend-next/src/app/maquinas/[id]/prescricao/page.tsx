import { z } from "zod";
import { AppShell } from "@/components/AppShell";
import { ErrorState, EmptyState } from "@/components/EmptyState";

const PrescricaoItemSchema = z.object({
  id: z.coerce.number(),
  maquina_id: z.string(),
  titulo: z.string(),
  descricao: z.string(),
  data_geracao: z.string(),
  status: z.enum(["pendente", "concluida", "cancelada"]),
});

const PrescricaoResponseSchema = z.array(PrescricaoItemSchema);

type PrescricaoItem = z.infer<typeof PrescricaoItemSchema>;

function resolveApiBase(): string {
  const env =
    process.env.NEXT_PUBLIC_FIELDNODE_SERVER_API_URL ??
    process.env.FIELDNODE_SERVER_API_URL ??
    "http://127.0.0.1:8000";
  return env.replace(/\/+$/, "");
}

export default async function PrescricaoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: maquinaId } = await params;
  const baseUrl = resolveApiBase();
  const prescricoesUrl = `${baseUrl}/api/prescricoes/?maquina_id=${encodeURIComponent(maquinaId)}`;

  let prescricoes: PrescricaoItem[] = [];

  try {
    const response = await fetch(prescricoesUrl, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(
        `Falha ao buscar prescrições: ${response.status} ${response.statusText}`,
      );
    }

    const raw = await response.json();
    prescricoes = PrescricaoResponseSchema.parse(raw);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Erro desconhecido";
    console.error("Erro ao buscar prescrições:", message);

    if (error instanceof z.ZodError) {
      return (
        <AppShell
          active="/colheitadeiras"
          eyebrow="Manutenção"
          title="Prescrições"
        >
          <ErrorState
            title="Resposta inesperada da API."
            message="A API retornou dados em formato não esperado."
          />
        </AppShell>
      );
    }

    return (
      <AppShell
        active="/colheitadeiras"
        eyebrow="Manutenção"
        title="Prescrições"
      >
        <ErrorState
          title="Não consegui carregar as prescrições."
          message={`${message} — confira se o backend está rodando, se o CORS está liberado para esta origem e tente novamente.`}
        />
      </AppShell>
    );
  }

  return (
    <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrições">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-50">
              Prescrições para {maquinaId}
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Recomendações de manutenção geradas pelo sistema.
            </p>
          </div>
          <a
            href="/colheitadeiras"
            className="rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]"
          >
            Voltar
          </a>
        </div>

        {prescricoes.length === 0 ? (
          <EmptyState
            title="Nenhuma prescrição encontrada."
            message="Nenhuma recomendação de manutenção foi gerada ou armazenada para esta máquina ainda."
          />
        ) : (
          <div className="space-y-4">
            {prescricoes.map((prescricao) => (
              <div
                key={prescricao.id}
                className="glass-panel rounded-lg p-5 border border-white/10 bg-white/[0.02]"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold text-slate-50">
                      {prescricao.titulo}
                    </h2>
                    <p className="mt-1 text-sm text-slate-400">
                      <span className="font-medium text-slate-300">Status:</span>{" "}
                      {prescricao.status.charAt(0).toUpperCase() +
                        prescricao.status.slice(1)}
                    </p>
                    <p className="mt-1 text-sm text-slate-400">
                      <span className="font-medium text-slate-300">Gerada em:</span>{" "}
                      {new Date(prescricao.data_geracao).toLocaleString("pt-BR")}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 rounded px-2.5 py-1 text-xs font-semibold border ${
                      prescricao.status === "pendente"
                        ? "bg-amber-500/15 text-amber-300 border-amber-500/30"
                        : prescricao.status === "concluida"
                          ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
                          : "bg-red-500/15 text-red-300 border-red-500/30"
                    }`}
                  >
                    {prescricao.status === "pendente"
                      ? "PENDENTE"
                      : prescricao.status === "concluida"
                        ? "CONCLUIDA"
                        : "CANCELADA"}
                  </span>
                </div>

                <p className="mt-4 text-sm text-slate-300">
                  {prescricao.descricao}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}

import { AppShell } from "@/components/AppShell";
import { ErrorState, EmptyState } from "@/components/EmptyState";

// Definir o tipo para a resposta da API de prescrições
type PrescricaoResponse = {
  id: number;
  colheitadeira: number;
  titulo: string;
  descricao: string;
  data_geracao: string;
  status: string;
};

export default async function PrescricaoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: maquinaId } = await params;

  const apiUrl =
    process.env.FIELDNODE_SERVER_API_URL || "http://web:8000/api";

  let prescricoes: PrescricaoResponse[] = [];

  try {
    const response = await fetch(
      `${apiUrl}/prescricoes/lista/?maquina_id=${encodeURIComponent(maquinaId)}`,
      {
        cache: "no-store",
        headers: { Accept: "application/json" },
      },
    );

    if (!response.ok) {
      throw new Error("Falha ao buscar prescrições");
    }

    prescricoes = await response.json();
  } catch (error) {
    console.error("Erro ao buscar prescrições:", error);
    return (
      <AppShell active="/colheitadeiras" eyebrow="Manutenção" title="Prescrições">
        <ErrorState
          title="Não consegui carregar as prescrições."
          message="Confira se o backend está rodando e tente novamente."
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

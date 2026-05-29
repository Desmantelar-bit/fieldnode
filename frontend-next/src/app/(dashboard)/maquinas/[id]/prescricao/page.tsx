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

  const apiUrl = process.env.FIELDNODE_SERVER_API_URL || "http://web:8000/api";

  let prescricoes: PrescricaoResponse[] = [];

  try {
    // Buscar prescrições armazenadas para esta máquina
    const response = await fetch(
      `${apiUrl}/prescricoes/?maquina_id=${encodeURIComponent(maquinaId)}`,
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
      <AppShell active="/dashboard" eyebrow="Manutencao" title="Prescricoes">
        <ErrorState
          title="Nao consegui carregar as prescricoes."
          message="Confira se o backend esta rodando e tente novamente."
        />
      </AppShell>
    );
  }

  return (
    <AppShell active="/dashboard" eyebrow="Manutencao" title="Prescricoes">
      <div className="space-y-6">
        {/* Cabeçalho com informações da máquina e botão de voltar */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-50">
              Prescricoes para {maquinaId}
            </h1>
            <p className="text-sm text-slate-400">
              Lista de recomendacoes de manutencao geradas pelo sistema
            </p>
          </div>
          <a
            href="/dashboard"
            className="px-4 py-2 bg-slate-800/20 border border-slate-700/30 rounded-md hover:bg-slate-800/30 text-sm font-medium transition-colors"
          >
            Voltar ao Dashboard
          </a>
        </div>

        {/* Lista de prescrições ou estado vazio */}
        {prescricoes.length === 0 ? (
          <EmptyState
            title="Nenhuma prescricao encontrada."
            message="Nenhuma recomendacao de manutencao foi gerada ou armazenada para esta máquina ainda."
          />
        ) : (
          <div className="space-y-4">
            {prescricoes.map((prescricao) => (
              <div
                key={prescricao.id}
                className="glass-panel rounded-lg p-5 border border-white/10 bg-white/[0.02] hover:border-white/5"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold text-slate-50">
                      {prescricao.titulo}
                    </h2>
                    <p className="text-sm text-slate-400 mb-2">
                      <span className="font-medium">Status:</span>
                      {prescricao.status.charAt(0).toUpperCase() +
                        prescricao.status.slice(1)}
                    </p>
                    <p className="text-sm text-slate-400">
                      <span className="font-medium">Gerada em:</span>
                      {new Date(prescricao.data_geracao).toLocaleDateString(
                        "pt-BR",
                      )}
                      {new Date(prescricao.data_geracao).toLocaleTimeString(
                        "pt-BR",
                      )}
                    </p>
                  </div>
                  {/* Badge de status */}
                  <span
                    className={`px-3 py-1 rounded text-xs font-semibold ${
                      prescricao.status === "pendente"
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        : prescricao.status === "concluida"
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "bg-red-500/20 text-red-400 border border-red-500/30"
                    }`}
                  >
                    {prescricao.status === "pendente"
                      ? "PENDENTE"
                      : prescricao.status === "concluida"
                        ? "CONCLUIDA"
                        : "CANCELADA"}
                  </span>
                </div>

                <div className="prose prose-sm max-w-none">
                  <p className="text-slate-400">{prescricao.descricao}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
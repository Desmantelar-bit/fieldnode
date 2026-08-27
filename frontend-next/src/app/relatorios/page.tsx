"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { ErrorState, EmptyState } from "@/components/EmptyState";
import { LoadingState } from "@/components/ui/FeedbackStates";
import { resolveApiUrl, telemetryService } from "@/services/telemetryService";
import type { Relatorio } from "@/types/telemetry";
import type { EstadoRequisicao } from "@/types/api";

type MachineOption = {
  id: number;
  maquina_id: string;
  modelo: string;
  marca: string;
};

const PERIOD_OPTIONS = [
  { label: "Ultimos 7 dias", value: 7 },
  { label: "Ultimos 15 dias", value: 15 },
  { label: "Ultimos 30 dias", value: 30 },
];

const API_URL = resolveApiUrl();

export default function RelatoriosPage() {
  const [estadoMaquinas, setEstadoMaquinas] = useState<EstadoRequisicao<MachineOption[]>>({ tipo: "carregando" });
  const [selectedMachine, setSelectedMachine] = useState("");
  const [search, setSearch] = useState("");
  const [period, setPeriod] = useState(7);
  const [estadoRelatorio, setEstadoRelatorio] = useState<EstadoRequisicao<Relatorio>>({ tipo: "vazio" });
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const filteredMachines = useMemo(() => {
    if (estadoMaquinas.tipo !== "sucesso") return [];
    const q = search.trim().toLowerCase();
    if (!q) return estadoMaquinas.dados;
    return estadoMaquinas.dados.filter((m) => {
      const haystack = `${m.maquina_id} ${m.modelo} ${m.marca}`.toLowerCase();
      return haystack.includes(q);
    });
  }, [estadoMaquinas, search]);

  useEffect(() => {
    telemetryService.getFleetStatus()
      .then((data) => {
        const options: MachineOption[] = data
          .filter((m) => m.maquina_id)
          .map((m) => ({
            id: m.id,
            maquina_id: m.maquina_id ?? "",
            modelo: m.modelo.nome,
            marca: m.modelo.marca.nome,
          }));
        if (options.length === 0) {
          setEstadoMaquinas({ tipo: "vazio" });
        } else {
          setEstadoMaquinas({ tipo: "sucesso", dados: options });
          setSelectedMachine(options[0].maquina_id);
        }
      })
      .catch((err: unknown) =>
        setEstadoMaquinas({
          tipo: "erro",
          mensagem: err instanceof Error ? err.message : "Erro ao carregar maquinas",
        })
      );
  }, []);

  const handleGenerate = async () => {
    if (!selectedMachine) return;
    setEstadoRelatorio({ tipo: "carregando" });
    setDownloadError(null);
    try {
      const data = await telemetryService.getRelatorio({
        machineId: selectedMachine,
        period,
      });
      if (data.status && data.status !== "ok") {
        throw new Error(data.detalhe || "Sem dados para o periodo selecionado");
      }
      setEstadoRelatorio({ tipo: "sucesso", dados: data });
    } catch (err) {
      setEstadoRelatorio({ tipo: "erro", mensagem: err instanceof Error ? err.message : "Erro ao gerar relatorio" });
    }
  };

  const downloadXlsx = async () => {
    if (!selectedMachine) return;
    setDownloadError(null);
    const fim = new Date();
    const inicio = new Date(fim);
    inicio.setDate(inicio.getDate() - period);
    const formatarData = (data: Date) => {
      const ano = data.getFullYear();
      const mes = String(data.getMonth() + 1).padStart(2, "0");
      const dia = String(data.getDate()).padStart(2, "0");
      return `${ano}-${mes}-${dia}`;
    };

    try {
      const res = await fetch(
        `${API_URL}/relatorio/exportar/?maquina_id=${encodeURIComponent(selectedMachine)}&data_inicio=${formatarData(inicio)}&data_fim=${formatarData(fim)}`,
        { headers: { Accept: "*/*" } },
      );
      if (!res.ok) throw new Error(String(res.status));
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `relatorio_${selectedMachine}_${period}d.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(url), 0);
    } catch {
      setDownloadError("Falha ao exportar o XLSX.");
    }
  };

  const toneClass = (value: number, thresholds: [number, number]) =>
    value > thresholds[1]
      ? "text-red-200"
      : value > thresholds[0]
        ? "text-amber-200"
        : "text-emerald-200";

  const relatorio = estadoRelatorio.tipo === "sucesso" ? estadoRelatorio.dados : null;

  return (
    <AppShell active="/relatorios" eyebrow="FieldNode" title="Relatorios">
      {estadoMaquinas.tipo === "carregando" && <LoadingState mensagem="Carregando frota..." />}
      {estadoMaquinas.tipo === "erro" && (
        <ErrorState title="Nao foi possivel carregar a frota." message={estadoMaquinas.mensagem} />
      )}
      {estadoMaquinas.tipo === "vazio" && (
        <EmptyState title="Nenhuma maquina cadastrada." message="Cadastre maquinas na API para gerar relatorios." />
      )}
      {estadoMaquinas.tipo === "sucesso" && (
      <div className="space-y-6">
        <section className="glass-panel rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-200">
            Configurar relatorio
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Selecione a maquina e o periodo para gerar o resumo operacional.
          </p>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Maquina
              </label>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por ID ou nome..."
                className="h-10 rounded-md border border-white/10 bg-black/30 px-3 text-sm text-slate-100 outline-none focus:border-emerald-300/40"
              />
              <select
                value={selectedMachine}
                onChange={(e) => {
                  setSelectedMachine(e.target.value);
                  setSearch("");
                }}
                className="h-10 rounded-md border border-white/10 bg-black/30 px-3 text-sm text-slate-100 outline-none focus:border-emerald-300/40"
              >
                {filteredMachines.length === 0 ? (
                  <option>Nenhuma maquina encontrada</option>
                ) : (
                  filteredMachines.map((m) => (
                    <option key={m.id} value={m.maquina_id}>
                      {m.maquina_id} - {m.marca} {m.modelo}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Periodo
              </label>
              <select
                value={period}
                onChange={(e) => setPeriod(Number(e.target.value))}
                className="h-10 rounded-md border border-white/10 bg-black/30 px-3 text-sm text-slate-100 outline-none focus:border-emerald-300/40"
              >
                {PERIOD_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-end gap-2">
              <button
                onClick={handleGenerate}
                disabled={estadoRelatorio.tipo === "carregando" || !selectedMachine}
                className="h-10 flex-1 rounded-md bg-emerald-600/20 px-4 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-600/30 disabled:opacity-50"
              >
                {estadoRelatorio.tipo === "carregando" ? "Gerando..." : "Gerar relatorio"}
              </button>
              {estadoRelatorio.tipo === "sucesso" && (
                <button
                  onClick={downloadXlsx}
                  className="h-10 rounded-md border border-white/10 bg-white/[0.04] px-3 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]"
                >
                  XLSX
                </button>
              )}
            </div>
          </div>
        </section>

        {downloadError && (
          <ErrorState title="Exportacao indisponivel" message={downloadError} />
        )}

        {estadoRelatorio.tipo === "carregando" && <LoadingState mensagem="Gerando relatorio..." />}

        {estadoRelatorio.tipo === "erro" && (
          <ErrorState title="Relatorio indisponivel" message={estadoRelatorio.mensagem} />
        )}

        {estadoRelatorio.tipo === "vazio" && (
          <EmptyState
            title="Nenhum relatorio gerado."
            message="Selecione a maquina e o periodo para visualizar as metricas operacionais."
          />
        )}

        {relatorio && (
          <>
            <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <div className="glass-panel rounded-lg p-5">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Leituras analisadas
                </p>
                <p className="mt-3 text-2xl font-semibold text-slate-50">
                  {relatorio.total_leituras}
                </p>
              </div>
              <div className="glass-panel rounded-lg p-5">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Maquinas ativas
                </p>
                <p className={`mt-3 text-2xl font-semibold ${toneClass(relatorio.maquinas_ativas, [0, 3])}`}>
                  {relatorio.maquinas_ativas}
                </p>
              </div>
              <div className="glass-panel rounded-lg p-5">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Alertas gerados
                </p>
                <p className={`mt-3 text-2xl font-semibold ${toneClass(relatorio.alertas_gerados, [5, 20])}`}>
                  {relatorio.alertas_gerados}
                </p>
              </div>
              <div className="glass-panel rounded-lg p-5">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Eficiencia
                </p>
                <p className={`mt-3 text-2xl font-semibold ${toneClass(relatorio.eficiencia_operacional, [50, 80])}`}>
                  {relatorio.eficiencia_operacional.toFixed(1)}%
                </p>
              </div>
            </section>

            <section className="glass-panel rounded-lg p-5">
              <h2 className="text-sm font-semibold text-slate-200">
                Resumo operacional
              </h2>
              <p className="mt-3 text-sm text-slate-300">
                O sistema encontrou {relatorio.total_leituras} leituras, {relatorio.maquinas_ativas} maquinas ativas e {relatorio.alertas_gerados} alertas no periodo analisado.
              </p>
              <p className="mt-4 text-[11px] text-slate-500">
                Periodo: {relatorio.periodo}
              </p>
            </section>
          </>
        )}
      </div>
      )}
    </AppShell>
  );
}

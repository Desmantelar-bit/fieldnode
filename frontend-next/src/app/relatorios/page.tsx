"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { ErrorState, EmptyState } from "@/components/EmptyState";

type MachineOption = {
  id: number;
  maquina_id: string;
  modelo: string;
  marca: string;
};

type ReportData = {
  status: string;
  maquina_id: string;
  periodo_dias: number;
  total_leituras: number;
  data_inicio: string;
  data_fim: string;
  dados: {
    horas_operadas: number;
    pico_temperatura: number;
    num_alertas: number;
    recomendacao_manutencao: string;
  };
};

const PERIOD_OPTIONS = [
  { label: "Últimos 7 dias", value: 7 },
  { label: "Últimos 15 dias", value: 15 },
  { label: "Últimos 30 dias", value: 30 },
];

function resolveApiUrl(): string {
  if (typeof window !== "undefined") return "http://localhost:8000/api";
  return process.env.NEXT_PUBLIC_API_URL || "http://web:8000/api";
}

export default function RelatoriosPage() {
  const [machines, setMachines] = useState<MachineOption[]>([]);
  const [selectedMachine, setSelectedMachine] = useState("");
  const [search, setSearch] = useState("");
  const [period, setPeriod] = useState(7);
  const [loading, setLoading] = useState(false);
  const [loadingMachines, setLoadingMachines] = useState(true);
  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = useMemo(() => resolveApiUrl(), []);

  const filteredMachines = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return machines;
    return machines.filter((m) => {
      const haystack = `${m.maquina_id} ${m.modelo} ${m.marca}`.toLowerCase();
      return haystack.includes(q);
    });
  }, [machines, search]);

  useEffect(() => {
    const fetchMachines = async () => {
      try {
        const res = await fetch(`${apiUrl}/colheitadeira/`, {
          cache: "no-store",
          headers: { Accept: "application/json" },
        });
        if (!res.ok) throw new Error("Falha ao buscar máquinas");
        const data = await res.json();
        const options: MachineOption[] = (data ?? [])
          .filter((m: any) => m.maquina_id)
          .map((m: any) => ({
            id: m.id,
            maquina_id: m.maquina_id,
            modelo: m.modelo?.nome ?? "Modelo não informado",
            marca: m.modelo?.marca?.nome ?? "Marca não informada",
          }));
        setMachines(options);
        if (options.length > 0) setSelectedMachine(options[0].maquina_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar máquinas");
      } finally {
        setLoadingMachines(false);
      }
    };
    fetchMachines();
  }, [apiUrl]);

  const handleGenerate = async () => {
    if (!selectedMachine) return;
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await fetch(
        `${apiUrl}/relatorio/?maquina_id=${encodeURIComponent(selectedMachine)}&periodo=${period}&formato=json`,
        { cache: "no-store", headers: { Accept: "application/json" } }
      );
      if (!res.ok) throw new Error(`Falha ao gerar relatório (${res.status})`);
      const data: ReportData = await res.json();
      if (data.status !== "ok") {
        throw new Error(data.detalhe || "Sem dados para o período selecionado");
      }
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar relatório");
    } finally {
      setLoading(false);
    }
  };

  const downloadCsv = async () => {
    if (!selectedMachine) return;
    const res = await fetch(
      `${apiUrl}/relatorio/?maquina_id=${encodeURIComponent(selectedMachine)}&periodo=${period}&formato=csv`
    );
    if (!res.ok) return;
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `relatorio_${selectedMachine}_${period}d.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const toneClass = (value: number, thresholds: [number, number]) =>
    value > thresholds[1]
      ? "text-red-200"
      : value > thresholds[0]
        ? "text-amber-200"
        : "text-emerald-200";

  return (
    <AppShell active="/relatorios" eyebrow="FieldNode" title="Relatórios">
      <div className="space-y-6">
        <section className="glass-panel rounded-lg p-5">
          <h2 className="text-sm font-semibold text-slate-200">Configurar relatório</h2>
          <p className="mt-1 text-xs text-slate-500">
            Selecione a máquina e o período para gerar o relatório operacional.
          </p>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Máquina
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
                disabled={loadingMachines}
                className="h-10 rounded-md border border-white/10 bg-black/30 px-3 text-sm text-slate-100 outline-none focus:border-emerald-300/40 disabled:opacity-50"
              >
                {loadingMachines ? (
                  <option>Carregando...</option>
                ) : filteredMachines.length === 0 ? (
                  <option>Nenhuma máquina encontrada</option>
                ) : (
                  filteredMachines.map((m) => (
                    <option key={m.id} value={m.maquina_id}>
                      {m.maquina_id} — {m.marca} {m.modelo}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Período
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
                disabled={loading || !selectedMachine}
                className="h-10 flex-1 rounded-md bg-emerald-600/20 px-4 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-600/30 disabled:opacity-50"
              >
                {loading ? "Gerando..." : "Gerar relatório"}
              </button>
              {report && (
                <button
                  onClick={downloadCsv}
                  className="h-10 rounded-md border border-white/10 bg-white/[0.04] px-3 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.08]"
                >
                  CSV
                </button>
              )}
            </div>
          </div>
        </section>

        {error && (
          <ErrorState title="Relatório indisponível" message={error} />
        )}

        {report && (
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Leituras analisadas
              </p>
              <p className="mt-3 text-2xl font-semibold text-slate-50">
                {report.dados.total_leituras ?? report.total_leituras}
              </p>
            </div>
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Horas operadas
              </p>
              <p
                className={`mt-3 text-2xl font-semibold ${toneClass(report.dados.horas_operadas, [20, 50])}`}
              >
                {report.dados.horas_operadas.toFixed(1)}h
              </p>
            </div>
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Pico de temperatura
              </p>
              <p
                className={`mt-3 text-2xl font-semibold ${toneClass(report.dados.pico_temperatura, [85, 110])}`}
              >
                {report.dados.pico_temperatura.toFixed(1)}°C
              </p>
            </div>
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Alertas no período
              </p>
              <p
                className={`mt-3 text-2xl font-semibold ${toneClass(report.dados.num_alertas, [5, 20])}`}
              >
                {report.dados.num_alertas}
              </p>
            </div>
          </section>
        )}

        {report && (
          <section className="glass-panel rounded-lg p-5">
            <h2 className="text-sm font-semibold text-slate-200">Recomendação de manutenção</h2>
            <p className="mt-3 text-sm text-slate-300">{report.dados.recomendacao_manutencao}</p>
            <p className="mt-4 text-[11px] text-slate-500">
              Período: {new Date(report.data_inicio).toLocaleDateString("pt-BR")} até{" "}
              {new Date(report.data_fim).toLocaleDateString("pt-BR")}
            </p>
          </section>
        )}

        {!report && !error && !loading && (
          <EmptyState
            title="Nenhum relatório gerado."
            message="Selecione a máquina e o período para visualizar as métricas operacionais."
          />
        )}
      </div>
    </AppShell>
  );
}

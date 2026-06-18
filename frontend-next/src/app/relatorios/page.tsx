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
  status?: string;
  detalhe?: string;
  periodo: string;
  total_leituras: number;
  maquinas_ativas: number;
  alertas_gerados: number;
  eficiencia_operacional: number;
};

const PERIOD_OPTIONS = [
  { label: "Ultimos 7 dias", value: 7 },
  { label: "Ultimos 15 dias", value: 15 },
  { label: "Ultimos 30 dias", value: 30 },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export default function RelatoriosPage() {
  const [machines, setMachines] = useState<MachineOption[]>([]);
  const [selectedMachine, setSelectedMachine] = useState("");
  const [search, setSearch] = useState("");
  const [period, setPeriod] = useState(7);
  const [loading, setLoading] = useState(false);
  const [loadingMachines, setLoadingMachines] = useState(true);
  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState<string | null>(null);

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
        const res = await fetch(`${API_URL}/colheitadeira/`, {
          cache: "no-store",
          headers: { Accept: "application/json" },
        });
        if (!res.ok) throw new Error("Falha ao buscar maquinas");
        const data = await res.json();
        const options: MachineOption[] = (data ?? [])
          .filter((m: { maquina_id?: string }) => m.maquina_id)
          .map((m: {
            id: number;
            maquina_id: string;
            modelo?: { nome?: string; marca?: { nome?: string } };
          }) => ({
            id: m.id,
            maquina_id: m.maquina_id,
            modelo: m.modelo?.nome ?? "Modelo nao informado",
            marca: m.modelo?.marca?.nome ?? "Marca nao informada",
          }));
        setMachines(options);
        if (options.length > 0) setSelectedMachine(options[0].maquina_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar maquinas");
      } finally {
        setLoadingMachines(false);
      }
    };
    fetchMachines();
  }, []);

  const handleGenerate = async () => {
    if (!selectedMachine) return;
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await fetch(
        `${API_URL}/relatorio/?maquina_id=${encodeURIComponent(selectedMachine)}&periodo=${period}&formato=json`,
        { cache: "no-store", headers: { Accept: "application/json" } },
      );
      if (!res.ok) throw new Error(`Falha ao gerar relatorio (${res.status})`);
      const data: ReportData = await res.json();
      if (data.status && data.status !== "ok") {
        throw new Error(data.detalhe || "Sem dados para o periodo selecionado");
      }
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar relatorio");
    } finally {
      setLoading(false);
    }
  };

  const downloadCsv = async () => {
    if (!selectedMachine) return;
    const res = await fetch(
      `${API_URL}/relatorio/?maquina_id=${encodeURIComponent(selectedMachine)}&periodo=${period}&formato=csv`,
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
    <AppShell active="/relatorios" eyebrow="FieldNode" title="Relatorios">
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
                disabled={loadingMachines}
                className="h-10 rounded-md border border-white/10 bg-black/30 px-3 text-sm text-slate-100 outline-none focus:border-emerald-300/40 disabled:opacity-50"
              >
                {loadingMachines ? (
                  <option>Carregando...</option>
                ) : filteredMachines.length === 0 ? (
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
                disabled={loading || !selectedMachine}
                className="h-10 flex-1 rounded-md bg-emerald-600/20 px-4 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-600/30 disabled:opacity-50"
              >
                {loading ? "Gerando..." : "Gerar relatorio"}
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

        {error && <ErrorState title="Relatorio indisponivel" message={error} />}

        {report && (
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Leituras analisadas
              </p>
              <p className="mt-3 text-2xl font-semibold text-slate-50">
                {report.total_leituras}
              </p>
            </div>
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Maquinas ativas
              </p>
              <p className={`mt-3 text-2xl font-semibold ${toneClass(report.maquinas_ativas, [0, 3])}`}>
                {report.maquinas_ativas}
              </p>
            </div>
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Alertas gerados
              </p>
              <p className={`mt-3 text-2xl font-semibold ${toneClass(report.alertas_gerados, [5, 20])}`}>
                {report.alertas_gerados}
              </p>
            </div>
            <div className="glass-panel rounded-lg p-5">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                Eficiencia
              </p>
              <p className={`mt-3 text-2xl font-semibold ${toneClass(report.eficiencia_operacional, [50, 80])}`}>
                {report.eficiencia_operacional.toFixed(1)}%
              </p>
            </div>
          </section>
        )}

        {report && (
          <section className="glass-panel rounded-lg p-5">
            <h2 className="text-sm font-semibold text-slate-200">
              Resumo operacional
            </h2>
            <p className="mt-3 text-sm text-slate-300">
              O sistema encontrou {report.total_leituras} leituras, {report.maquinas_ativas} maquinas ativas e {report.alertas_gerados} alertas no periodo analisado.
            </p>
            <p className="mt-4 text-[11px] text-slate-500">
              Periodo: {report.periodo}
            </p>
          </section>
        )}

        {!report && !error && !loading && (
          <EmptyState
            title="Nenhum relatorio gerado."
            message="Selecione a maquina e o periodo para visualizar as metricas operacionais."
          />
        )}
      </div>
    </AppShell>
  );
}

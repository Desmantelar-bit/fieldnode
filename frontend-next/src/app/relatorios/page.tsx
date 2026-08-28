"use client";

import { useEffect, useMemo, useState } from "react";
import { Download, FileText } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { telemetryService } from "@/services/telemetryService";
import type { EstadoRequisicao } from "@/types/api";
import type { Relatorio } from "@/types/telemetry";

type MachineOption = { id: number; maquina_id: string; modelo: string; marca: string };

const PERIOD_OPTIONS = [
  { label: "Últimos 7 dias", value: 7 },
  { label: "Últimos 15 dias", value: 15 },
  { label: "Últimos 30 dias", value: 30 },
];

function resolveExportUrl(machineId: string) {
  const apiUrl = (process.env.NEXT_PUBLIC_API_URL || "/api").replace(/\/+$/, "");
  const baseUrl = apiUrl.endsWith("/api") ? apiUrl : `${apiUrl}/api`;
  return `${baseUrl}/relatorio/exportar/?maquina_id=${encodeURIComponent(machineId)}`;
}

export default function RelatoriosPage() {
  const [estadoMaquinas, setEstadoMaquinas] = useState<EstadoRequisicao<MachineOption[]>>({ tipo: "carregando" });
  const [selectedMachine, setSelectedMachine] = useState("");
  const [period, setPeriod] = useState(7);
  const [estadoRelatorio, setEstadoRelatorio] = useState<EstadoRequisicao<Relatorio>>({ tipo: "vazio" });

  useEffect(() => {
    let active = true;
    telemetryService.getFleetStatus()
      .then((machines) => {
        if (!active) return;
        const options = machines.filter((machine) => machine.maquina_id).map((machine) => ({
          id: machine.id,
          maquina_id: machine.maquina_id ?? "",
          modelo: machine.modelo.nome,
          marca: machine.modelo.marca.nome,
        }));
        setEstadoMaquinas(options.length ? { tipo: "sucesso", dados: options } : { tipo: "vazio" });
        setSelectedMachine(options[0]?.maquina_id ?? "");
      })
      .catch((error: unknown) => {
        if (active) setEstadoMaquinas({
          tipo: "erro",
          mensagem: error instanceof Error ? error.message : "Não foi possível carregar a frota.",
        });
      });
    return () => { active = false; };
  }, []);

  const relatorio = estadoRelatorio.tipo === "sucesso" ? estadoRelatorio.dados : null;
  const tableRows = useMemo(() => relatorio ? [
    ["Leituras analisadas", String(relatorio.total_leituras), "Volume consolidado no período"],
    ["Máquinas ativas", String(relatorio.maquinas_ativas), "Frota com telemetria no período"],
    ["Alertas gerados", String(relatorio.alertas_gerados), "Anomalias identificadas"],
    ["Eficiência operacional", `${relatorio.eficiencia_operacional.toFixed(1)}%`, "Índice operacional consolidado"],
  ] : [], [relatorio]);

  const handleGenerate = async () => {
    if (!selectedMachine) return;
    setEstadoRelatorio({ tipo: "carregando" });
    try {
      const data = await telemetryService.getRelatorio({ machineId: selectedMachine, period });
      if (data.status && data.status !== "ok") throw new Error(data.detalhe || "Sem dados para o período selecionado.");
      setEstadoRelatorio({ tipo: "sucesso", dados: data });
    } catch (error) {
      setEstadoRelatorio({ tipo: "erro", mensagem: error instanceof Error ? error.message : "Não foi possível gerar o relatório." });
    }
  };

  const handleExport = () => {
    if (selectedMachine) window.location.assign(resolveExportUrl(selectedMachine));
  };

  return (
    <main className="min-h-screen bg-base-950 p-5 text-white sm:p-8 lg:ml-28">
      <Sidebar />
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-status-normal">FieldNode</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-white">Relatórios operacionais</h1>
          <p className="mt-1 text-sm text-slate-400">Exportação e consolidação de dados analíticos da frota.</p>
        </header>

        <section className="rounded-3xl border border-white/20 bg-slate-50 p-5 text-slate-900 shadow-2xl sm:p-8">
          <div className="flex flex-col justify-between gap-5 border-b border-slate-200 pb-6 lg:flex-row lg:items-center">
            <div className="flex items-start gap-3">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-status-normal">
                <FileText aria-hidden="true" size={20} />
              </div>
              <div>
                <h2 className="text-lg font-bold">Consolidado de telemetria</h2>
                <p className="mt-1 text-xs text-slate-500">Métricas brutas e histórico de anomalias por máquina.</p>
              </div>
            </div>
            <button type="button" onClick={handleExport} disabled={!selectedMachine} className="inline-flex items-center justify-center gap-2 rounded-full bg-slate-900 px-6 py-3 text-sm font-medium text-white shadow-lg shadow-slate-900/10 transition-colors hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 disabled:cursor-not-allowed disabled:opacity-50">
              <Download aria-hidden="true" size={16} /> Exportar relatório XLSX
            </button>
          </div>

          {estadoMaquinas.tipo === "carregando" && <p className="py-8 text-sm text-slate-500">Carregando frota...</p>}
          {estadoMaquinas.tipo === "erro" && <p role="alert" className="py-8 text-sm text-red-700">{estadoMaquinas.mensagem}</p>}
          {estadoMaquinas.tipo === "vazio" && <p className="py-8 text-sm text-slate-500">Nenhuma máquina cadastrada para gerar relatórios.</p>}

          {estadoMaquinas.tipo === "sucesso" && (
            <>
              <div className="mt-6 grid gap-4 md:grid-cols-[minmax(0,1fr)_12rem_auto] md:items-end">
                <label className="grid gap-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Máquina
                  <select value={selectedMachine} onChange={(event) => setSelectedMachine(event.target.value)} className="h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm font-medium normal-case tracking-normal text-slate-900 outline-none transition focus:border-slate-900">
                    {estadoMaquinas.dados.map((machine) => <option key={machine.id} value={machine.maquina_id}>{machine.maquina_id} · {machine.marca} {machine.modelo}</option>)}
                  </select>
                </label>
                <label className="grid gap-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                  Período
                  <select value={period} onChange={(event) => setPeriod(Number(event.target.value))} className="h-11 rounded-xl border border-slate-200 bg-white px-3 text-sm font-medium normal-case tracking-normal text-slate-900 outline-none transition focus:border-slate-900">
                    {PERIOD_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </label>
                <button type="button" onClick={handleGenerate} disabled={estadoRelatorio.tipo === "carregando"} className="rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-900 transition hover:border-slate-900 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50">
                  {estadoRelatorio.tipo === "carregando" ? "Gerando..." : "Atualizar dados"}
                </button>
              </div>

              {estadoRelatorio.tipo === "erro" && <p role="alert" className="mt-5 text-sm text-red-700">{estadoRelatorio.mensagem}</p>}
              {estadoRelatorio.tipo === "vazio" && <p className="mt-8 text-sm text-slate-500">Selecione os filtros e atualize os dados para visualizar o consolidado.</p>}

              {relatorio && (
                <div className="mt-8 overflow-x-auto">
                  <table className="w-full min-w-[38rem] text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
                        <th className="pb-3 font-semibold">Métrica</th><th className="pb-3 font-semibold">Valor</th><th className="pb-3 font-semibold">Contexto</th><th className="pb-3 font-semibold">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {tableRows.map(([metric, value, context]) => (
                        <tr key={metric}>
                          <td className="py-4 font-medium text-slate-900">{metric}</td><td className="py-4 font-semibold text-slate-900">{value}</td><td className="py-4">{context}</td>
                          <td className="py-4"><span className="inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-800">Consolidado</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="mt-5 text-xs text-slate-500">Período analisado: {relatorio.periodo}</p>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
}

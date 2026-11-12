"use client";
import React, { useState } from "react";

export default function RelatoriosPage() {
  const [maquinaId, setMaquinaId] = useState("");
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");

  const handleDownload = async () => {
    if (!maquinaId) return alert("Selecione uma máquina");

    setStatus("loading");
    try {
      const response = await fetch(
        `/api/relatorios?maquina_id=${maquinaId}&tipo=csv`,
      );
      if (!response.ok) throw new Error();

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `relatorio_${maquinaId}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();

      setStatus("success");
    } catch (error) {
      setStatus("error");
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Extração de Relatórios</h1>
      <div className="bg-white p-6 rounded-xl shadow-md space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            ID da Máquina
          </label>
          <input
            type="text"
            className="mt-1 block w-full border rounded-md p-2"
            value={maquinaId}
            onChange={(e) => setMaquinaId(e.target.value)}
            placeholder="Ex: JD-8400"
          />
        </div>

        <button
          onClick={handleDownload}
          disabled={status === "loading"}
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition disabled:bg-gray-400"
        >
          {status === "loading" ? "Gerando..." : "Baixar Relatório (CSV)"}
        </button>

        {status === "success" && (
          <p className="text-green-600 text-center">
            Relatório gerado com sucesso!
          </p>
        )}
        {status === "error" && (
          <p className="text-red-600 text-center">
            Erro ao gerar relatório. Tente novamente.
          </p>
        )}
      </div>
    </div>
  );
}
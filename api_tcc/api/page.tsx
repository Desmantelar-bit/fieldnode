'use client';

import { useState } from 'react';

export default function CadastroColheitadeira() {
  const [formData, setFormData] = useState({
    modelo_id: '',
    combustivel_id: '',
    operario_id: '',
    // Outros campos omitidos para brevidade, mas seguem a mesma lógica
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:8000/api/colheitadeiras/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert('Colheitadeira cadastrada com sucesso!');
      }
    } catch (error) {
      console.error('Erro ao cadastrar:', error);
    }
  };

  // Exemplo de ajuste solicitado para a função cadastrarModelo
  const handleCadastrarModelo = async (nomeModelo: string, marcaId: number) => {
    const payload = {
      nome: nomeModelo,
      marca_id: marcaId, // Alterado de 'marca' para 'marca_id'
    };

    await fetch('http://localhost:8000/api/modelos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Cadastro de Colheitadeira</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block">ID do Modelo:</label>
          <input
            type="number"
            className="border p-2 rounded w-full"
            value={formData.modelo_id}
            onChange={(e) => setFormData({...formData, modelo_id: e.target.value})}
            required
          />
        </div>
        <div>
          <label className="block">ID do Operário:</label>
          <input
            type="number"
            className="border p-2 rounded w-full"
            value={formData.operario_id}
            onChange={(e) => setFormData({...formData, operario_id: e.target.value})}
            required
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Salvar Máquina
        </button>
      </form>
    </div>
  );
}
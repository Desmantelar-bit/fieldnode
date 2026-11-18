export type GraphMachine = { id: string; external_code: string; tipo: string | null };
export type GraphFront = { id: string; nome: string; codigo: string };
export type GraphLink = { id: string; origem: string; destino: string; tipo: string; front: string | null; de: string; ate: string | null };
export type OperationGraph = { machines: GraphMachine[]; fronts: GraphFront[]; links: GraphLink[] };

async function responseJson(response: Response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || 'Não foi possível atualizar as relações.');
  return payload;
}

export const operationGraphService = {
  async get(): Promise<OperationGraph> {
    const response = await fetch('/api/operation-graph/', { cache: 'no-store', headers: { Accept: 'application/json' } });
    return responseJson(response);
  },
  async create(payload: { origem: string; destino: string; tipo: string; front?: string; de: string; ate?: string }) {
    const response = await fetch('/api/operation-graph/', { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-FieldNode-CSRF': '1' }, body: JSON.stringify(payload) });
    return responseJson(response);
  },
  async importCsv(file: File) {
    const form = new FormData(); form.append('file', file);
    const response = await fetch('/api/operation-graph/import/', { method: 'POST', headers: { Accept: 'application/json', 'X-FieldNode-CSRF': '1' }, body: form });
    return responseJson(response);
  },
};

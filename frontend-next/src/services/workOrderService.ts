export type WorkOrder = {
  id: string; decision_id: string; titulo: string; descricao: string;
  machine: string; machine_external_code: string;
  responsavel: { id: string; nome: string; funcao: string; tipo: string } | null;
  prazo: string; status: string; prioridade: string; criado_em: string;
  concluida_em: string | null; conflito_responsavel?: boolean;
};

export async function listWorkOrders(params: Record<string, string>): Promise<{ results: WorkOrder[]; count: number }> {
  const query = new URLSearchParams(params);
  const response = await fetch(`/api/workorders/?${query.toString()}`, { cache: 'no-store', headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`Não foi possível carregar as ordens (${response.status}).`);
  return response.json() as Promise<{ results: WorkOrder[]; count: number }>;
}

export async function updateWorkOrder(id: string, payload: { prazo?: string; status?: string }): Promise<WorkOrder> {
  const response = await fetch(`/api/workorders/${id}/`, { method: 'PATCH', headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-FieldNode-CSRF': '1' }, body: JSON.stringify(payload) });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detalhe || `Não foi possível atualizar a OS (${response.status}).`);
  return body as WorkOrder;
}

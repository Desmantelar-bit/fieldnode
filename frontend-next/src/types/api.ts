export type EstadoRequisicao<T> =
  | { tipo: 'carregando' }
  | { tipo: 'sucesso'; dados: T }
  | { tipo: 'vazio' }
  | { tipo: 'erro'; mensagem: string };

export function mensagemErroRequisicao(
  erro: unknown,
  fallback = 'Nao foi possivel carregar os dados.',
) {
  return erro instanceof Error && erro.message ? erro.message : fallback;
}

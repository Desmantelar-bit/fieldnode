export type TrustFactorDefinition = { title: string; description: string };

export const trustFactorLabels: Record<string, TrustFactorDefinition> = {
  RELOGIO_NAO_CONFIAVEL: { title: 'Horário do dispositivo sem sincronização confiável', description: 'A leitura foi recebida com fonte de tempo não sincronizada.' },
  GAP_TEMPORAL: { title: 'Intervalo maior entre leituras', description: 'O cálculo registrou um intervalo temporal acima da heurística esperada.' },
  TIMESTAMP_FORA_DE_ORDEM: { title: 'Horário fora de ordem', description: 'O horário desta leitura antecede o da leitura usada como referência.' },
  TIMESTAMP_INDISPONIVEL: { title: 'Horário indisponível', description: 'Não havia dois horários válidos para avaliar a sequência.' },
  VALORES_REPETIDOS: { title: 'Valores repetidos', description: 'Um ou mais valores se repetiram consecutivamente; isso sinaliza uma verificação da leitura.' },
  PROXIMO_LIMITE_FISICO: { title: 'Próximo ao limite conhecido', description: 'A leitura ficou próxima a um limite físico configurado.' },
  SALTO_ABRUPTO: { title: 'Mudança abrupta', description: 'Foi registrada uma mudança grande em relação à leitura anterior.' },
  CONTINUIDADE_SUAVE: { title: 'Continuidade suave', description: 'Os valores comparáveis mudaram pouco em relação à leitura anterior.' },
  PRIMEIRA_LEITURA: { title: 'Primeira leitura', description: 'Ainda não havia leitura anterior para comparação.' },
};

export function describeTrustFactor(code: string): TrustFactorDefinition {
  return trustFactorLabels[code] ?? { title: `Outro fator (${code})`, description: 'O backend enviou um código ainda não conhecido por esta interface.' };
}

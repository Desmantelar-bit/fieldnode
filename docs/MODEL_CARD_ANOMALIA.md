# Model card: Isolation Forest de anomalias

## Identificação

- **Modelo:** Isolation Forest, detector não supervisionado.
- **Implementação:** `api_tcc/services/anomaly_detection.py`.
- **Versão do contrato:** `anomalia-v1`.
- **Semente:** `42`.
- **Contaminação:** `0.05`.

## Uso pretendido

Sinalizar padrões atípicos em leituras históricas de uma máquina e apoiar triagem operacional. O modelo não substitui inspeção, regra de segurança nem aprovação humana.

## Dados e treino

As entradas oficiais são `temperatura`, `vibracao` e `rpm`. O treino é feito por máquina/regime com histórico elegível e sem rótulo de falha. Média e desvio-padrão são calculados no histórico de treino e persistidos com o artefato.

## Saída

O modelo retorna `anomaly_score`, método de detecção, feature contribuinte e estado. Score alto significa maior atipicidade relativa ao histórico usado, não maior probabilidade de quebra.

## Evidências

O benchmark sintético verifica contrato, determinismo e métricas. A avaliação independente CWRU, quando executada com arquivos baixados da fonte oficial, compara o detector com um limiar simples sobre RMS, pico e curtose de Pearson. Os resultados ficam em `docs/evidence/s5/S5-T5_PUBLIC_CWRU_RESULTS.json` e no relatório de anomalias.

## Fora de escopo e limitações

Este modelo não estima data de falha, probabilidade de quebra ou RUL. Não diagnostica causa, não prova causalidade, não garante detecção de todos os defeitos e não demonstra transferência de desempenho para colheitadeiras. Mudança de regime, drift, histórico curto e sensores ruins podem gerar falsos positivos ou falsos negativos.

## Governança

Artefatos experimentais não substituem o registry de produção. Resultados devem preservar a partição treino/teste, hashes, parâmetros, semente e limitações. Nenhum resultado público autoriza afirmar validação em campo.

# Avaliação de anomalias

**Métrica de teste sintético, não de campo.**

Benchmark fixado: `benchmark_v1`; 8 cenários × 20 sementes.
O treino usa uma série normal independente por semente e não lê os rótulos de avaliação.

| Cenário | Execuções | TP | FP | FN | TN | Precisão média | Recall médio | F1 médio | FP/h média | Método | Versão |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| normal | 20 | 0 | 326 | 0 | 5674 | 0.000 | n/d | n/d | 3.271 | ISOLATION_FOREST | synthetic-if-v1 |
| subida_gradual | 20 | 343 | 225 | 1657 | 3775 | 0.590 | 0.171 | 0.262 | 2.258 | ISOLATION_FOREST | synthetic-if-v1 |
| pico_isolado | 20 | 20 | 324 | 0 | 5656 | 0.063 | 1.000 | 0.118 | 3.251 | ISOLATION_FOREST | synthetic-if-v1 |
| sensor_travado | 20 | 46 | 292 | 554 | 5108 | 0.088 | 0.077 | 0.119 | 2.930 | ISOLATION_FOREST | synthetic-if-v1 |
| lacuna_comunicacao | 20 | 0 | 293 | 0 | 4907 | 0.000 | n/d | n/d | 2.940 | ISOLATION_FOREST | synthetic-if-v1 |
| maquina_desligada | 20 | 0 | 2225 | 0 | 3775 | 0.000 | n/d | n/d | 22.324 | ISOLATION_FOREST | synthetic-if-v1 |
| subida_gradual_fora_de_ordem | 20 | 343 | 225 | 1657 | 3775 | 0.590 | 0.171 | 0.262 | 2.258 | ISOLATION_FOREST | synthetic-if-v1 |
| mudanca_de_carga | 20 | 0 | 2225 | 0 | 3775 | 0.000 | n/d | n/d | 22.324 | ISOLATION_FOREST | synthetic-if-v1 |

## Limitações

Os dados são sintéticos e servem para verificar determinismo, contrato e cálculo das métricas. Não são validação de campo, não medem falha mecânica e não autorizam afirmar previsão de falhas.

A lacuna de comunicação é tratada como caso de observabilidade; ausência de leitura não é convertida silenciosamente em normalidade.

## S5-T5 - avaliação independente em dataset público

### Decisão D-18 e auditoria dos candidatos

| Candidato | Disponibilidade verificada em 15/11/2026 | Licença/uso | Compatibilidade | Decisão |
|---|---|---|---|---|
| CWRU Bearing Data Center | Página oficial disponível; arquivos `.mat` são oferecidos por grupos de condição e carga. Os binários não foram empacotados neste repositório. | A página oficial consultada descreve os dados e links de download, mas não declara uma licença aberta. Uso condicionado à observação dos termos da fonte e download manual. | Sinal bruto de vibração, 12 kHz/48 kHz conforme o grupo, com condições normal e defeituosa documentadas. Permite RMS, pico e curtose por janela. | **Escolhido para S5-T5**, com restrição de redistribuição e execução local pendente dos arquivos. |
| AI4I 2020 | CSV oficial disponível na UCI, 10.000 linhas. | CC BY 4.0, com atribuição. | O próprio UCI informa que é sintético; dados tabulares não são sinal bruto de vibração, portanto RMS/pico/curtose por janela não seriam fisicamente justificáveis. | Não escolhido como evidência principal de falha real. |

Fontes auditadas: [CWRU Data Center](https://engineering.case.edu/bearingdatacenter/download-data-file) e [UCI AI4I 2020](https://archive.ics.uci.edu/dataset/601/ai4i). A página do CWRU informa formato Matlab, variáveis de vibração e taxas de amostragem; a UCI informa explicitamente a natureza sintética do AI4I e sua licença CC BY 4.0.

### Implementação e protocolo

`ml/eval/public_dataset.py` carrega os `.mat` informados pelo operador, identifica a série `_DE_time` ou `_FE_time`, descarta janelas incompletas ou não finitas e extrai RMS, pico e curtose de Pearson. O treino usa apenas arquivos normais indicados em `--train-normal`; o teste usa arquivos normais e defeituosos separados. A unidade de análise é a janela e os arquivos são preservados nos hashes SHA-256 do resultado.

O Isolation Forest reutiliza o contrato oficial de `api_tcc.services.anomaly_detection.detect_many_from_history`, com adaptador explícito de nomes de features. O baseline é um limiar transparente de z-score máximo `>= 3.0`, calibrado somente no conjunto normal de treino. Ambos usam a mesma partição e a mesma definição de rótulo.

Execução, depois de baixar os arquivos autorizados da fonte oficial:

```text
python -m ml.eval.public_dataset --train-normal data/cwru/Normal_0.mat --test-normal data/cwru/Normal_1.mat --test-fault data/cwru/IR007_0.mat --output docs/evidence/s5/S5-T5_PUBLIC_CWRU_RESULTS.json
```

O comando acima é um exemplo de forma; os nomes devem ser substituídos pelos arquivos realmente baixados. O Makefile expõe `eval-public` para inspeção do comando, sem download silencioso.

### Estado da evidência

**IMPLEMENTAÇÃO VERIFICADA. EXECUÇÃO CWRU REAL: NÃO VERIFICADA.** Os arquivos binários oficiais não estavam disponíveis localmente durante esta entrega, portanto não há métricas IF versus limiar publicadas. Os testes usam fixtures numéricas pequenas e verificam extração, janela incompleta, valores inválidos, reprodutibilidade e comparação dos dois métodos; eles não substituem a execução no CWRU.

Este experimento valida aspectos da metodologia de detecção em um dataset público de domínio industrial distinto. Ele não comprova a eficácia do produto FieldNode em colheitadeiras, nem demonstra transferência direta de desempenho para máquinas agrícolas.

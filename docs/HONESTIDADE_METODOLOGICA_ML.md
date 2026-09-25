# Honestidade metodológica em ML

**Escopo da auditoria:** estado do checkout em 25/09/2026. Foram inspecionados os módulos de análise encontrados sob `api_tcc/ia/`, o detector em `api_tcc/services/anomaly_detection.py`, o serviço legado de prescrição, modelos `Event`/`Decision`, README e referências de treinamento. Os caminhos citados no planejamento (`ia/anomalias.py`, `ia/manutencao.py`, `ia/prescricoes.py`) não existem neste checkout. Portanto, este documento descreve o código encontrado, não presume que a descrição do planejamento corresponda à implementação atual.

## Resumo

O repositório contém detecção não supervisionada de anomalias com Isolation Forest e decisões operacionais baseadas em thresholds/regras determinísticas. Não foi encontrado `RandomForestClassifier`, nem módulo de manutenção supervisionada, nem evidência de dataset rotulado de falhas usado para treinar um classificador. Assim, o checkout não sustenta a alegação de que um modelo supervisionado prevê falhas mecânicas.

Há duas implementações de detecção com Isolation Forest: um modelo persistido, treinado por comando de gerenciamento, e um detector por máquina que mantém estado em memória e treina ao atingir o mínimo de histórico. Eles não devem ser confundidos. O primeiro usa três sensores e dados descritos como cenário normal de bancada; o segundo usa histórico de telemetria daquela máquina. Em ambos, anomalia significa comportamento incomum segundo a referência usada, não falha mecânica confirmada nem previsão de evento futuro.

## Comparação dos componentes encontrados

| Componente | Algoritmo / lógica | Tipo | Dados utilizados | Rótulo | Treinamento | Prediz falha mecânica? | Confiança metodológica atual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `api_tcc/ia/deteccao_multivariada.py` | Isolation Forest, 100 estimadores, `contamination=0.05`, `random_state=42` | Detecção de anomalias não supervisionada | Colunas `temperatura`, `vibracao`, `rpm` de um DataFrame. O comando gera cenário sintético com distribuições uniformes independentes: temperatura 60–80, vibração 0,2–2,0 e RPM 1400–1900. Padrões/correlações reais não são representados por esse gerador. Não há normalização explícita neste módulo. | Não usa rótulo de falha; o conjunto é descrito como normal para o treinamento | `treinar_modelo(df_normal)` chama `fit`, persiste via `joblib` em `api_tcc/ia/modelos/isolation_forest_v1.pkl`; inferência carrega o arquivo. O comando `treinar_isolation_forest` aceita `--leituras` (padrão 1000, mínimo 100) e gera dados com seed 42. | Não. Sinaliza observações atípicas em relação ao treino. | Adequado como demonstração técnica de detecção não supervisionada em dados sintéticos; não há evidência de validade operacional. |
| `api_tcc/services/anomaly_detection.py` | Isolation Forest após padronização por média/desvio do histórico; fallback inicial por z-score | Detecção não supervisionada com fallback estatístico determinístico | Histórico de `LeituraTelemetria` da máquina: `temperatura`, `vibracao`, `rpm`. Ausências no vetor atual são preenchidas pela média histórica. Com menos de 100 leituras usa z-score; a partir daí treina o Isolation Forest em memória. | Não usa rótulos de falha | O registro em memória é por processo e máquina. O modelo é ajustado na primeira detecção com histórico suficiente, não é persistido em disco neste serviço. `contamination=0.05`, `random_state=42`. | Não. A função retorna sinal/score de anomalia, não probabilidade de falha futura. | Coerente como sinal exploratório; baseline e comportamento dependem da janela histórica disponível e do ciclo de vida do processo. |
| `api_tcc/ia/pipeline.py` | Regras de threshold e contagem de motivos; Isolation Forest como sinal adicional | Híbrido, com decisão final determinística | Janela de até 500 leituras (`temperatura`, `vibracao`, `rpm`), features agregadas e leitura mais recente. | Não há label de treino | Calcula features; marca motivos por `temp_max > 85`, `temp_tendencia > 0.5`, `vib_media > 5`; consulta o modelo multivariado se disponível. Um motivo vira `ATENCAO`, dois ou mais `CRITICO`; zero vira `NORMAL`. | Não. Classifica estado conforme regras/sinais atuais. | Fluxo de triagem determinístico; thresholds são de prototipação conforme comentário e `docs/limiares.md`. O sinal ML não determina sozinho a severidade. |
| `api_tcc/services/prescricao.py` | Thresholds determinísticos (`temp_media > 95`, `vibracao_max > 8.0`) | Regras | Até 10 leituras recentes | Não se aplica | Não há treinamento nem modelo ML. O próprio módulo se declara legado e fora das rotas atuais. | Não. Cria sugestões condicionais, não previsão de falha. | Regra explícita de protótipo/legado; não confundir com o pipeline operacional atual. |
| Manutenção supervisionada / `RandomForestClassifier` | Não localizado no código deste checkout | Não demonstrado | Não identificado | Não identificado | Não identificado | Não há base para afirmar que existe | Não avaliável; qualquer menção no README deve ser tratada como desatualizada até que uma implementação seja localizada e auditada. |

## O que cada método permite concluir

### Regras determinísticas

Uma regra associa condições explícitas a uma saída. No pipeline atual, os limites e a quantidade de motivos determinam `NORMAL`, `ATENCAO` ou `CRITICO`. Isso é lógica determinística, não aprendizado de máquina. Os limites são descritos no código como prototipação e remetem a `docs/limiares.md`; não são limites universais de segurança para máquinas agrícolas.

### Detecção de anomalias

Isolation Forest identifica observações que parecem isoladas em relação aos dados usados como referência. O detector por máquina também usa z-score durante o cold start. Isso pode priorizar investigação, mas não estabelece que houve falha, sua causa ou que uma falha ocorrerá. Um valor atípico pode ser condição operacional legítima; uma falha também pode ocorrer sem gerar um padrão detectado.

### Predição supervisionada

Um classificador supervisionado aprende a relação entre entradas e rótulos observados. Para falar em previsão de manutenção, os rótulos devem representar eventos operacionais rastreáveis, com definição e janela temporal claras, e a avaliação deve separar dados de treino e validação de forma compatível com a ordem temporal e as máquinas. Não foi encontrada essa implementação ou evidência de avaliação neste checkout.

## Dados, treino e avaliação observados

- O modelo persistido em `deteccao_multivariada.py` recebe um DataFrame com três colunas. O comando `treinar_isolation_forest` gera dados sintéticos independentes por distribuição uniforme, com padrão de 1000 linhas, mínimo de 100 e seed 42. Isso não equivale a medições de máquinas reais nem captura correlações entre sensores. O trainer também pode ser chamado com outro DataFrame pelo código.
- O detector em `services/anomaly_detection.py` consulta leituras armazenadas para a máquina, percorre o histórico disponível e só ajusta Isolation Forest quando há pelo menos 100 leituras. Não há amostragem temporal, limite de janela ou persistência de modelo neste serviço. O estado é em memória do processo.
- `contamination=0.05` é parâmetro de ajuste do Isolation Forest, não uma taxa de falhas medida no campo nem uma métrica de qualidade.
- Foi encontrado `random_state=42` nos dois treinadores Isolation Forest. Não foi encontrada avaliação por conjunto independente, validação cruzada, avaliação temporal ou métricas de produção nesses componentes.
- Não foi encontrado pipeline de treino ou avaliação de Random Forest, `train_test_split`, métricas de classificação, nem rótulo mecânico real associado a esse modelo.
- A padronização explícita está presente no detector por máquina, usando média e desvio do histórico. Não está presente no trainer persistido de `deteccao_multivariada.py`.

## Quem determina a severidade e a prescrição

Em `api_tcc/ia/pipeline.py`, Isolation Forest é um sinal complementar. O resultado só é acrescentado como motivo quando detecta anomalia e nenhuma regra anterior já produziu motivo. A severidade final é determinada pela contagem de motivos (`classificar_risco`), não por um classificador supervisionado. A recomendação textual é então escolhida pelo status.

O serviço `api_tcc/services/prescricao.py` é explicitamente marcado como legado e informa que não é usado pelas rotas atuais. Ele cria registros `Prescricao` a partir de dois thresholds. A persistência operacional contemporânea de decisões está modelada separadamente em `Event` e `Decision`; `Decision` registra status e `outcome_texto`. Isso constitui infraestrutura para feedback, não um dataset rotulado validado nem uma ligação automática entre resultado e falha mecânica.

## Formulações permitidas

| Formulação | Situação neste checkout |
| --- | --- |
| “Usa Isolation Forest para detecção não supervisionada de anomalias em três sinais de telemetria” | Sustentada pelos módulos encontrados; especificar qual implementação ao descrever treino e ciclo de vida. |
| “Usa regras determinísticas de thresholds para classificar o estado operacional” | Sustentada pelo pipeline. Informar que os thresholds são de prototipação. |
| “O Isolation Forest prevê falha mecânica” | Não sustentada. Anomalia não equivale a falha ou previsão futura. |
| “Random Forest treinado com falhas reais” | Não sustentada pelo checkout; o algoritmo não foi localizado. |
| “Previsão de manutenção com IA” ou “modelo preditivo de falhas” | Evitar até existir dataset operacional rotulado, protocolo de validação e evidência de desempenho. |
| “O feedback de operadores já treina o modelo” | Não sustentada. `Decision.status` e `outcome_texto` são matéria-prima potencial, ainda não dataset supervisionado. |

Formulação recomendada para descrever o estado atual: **“classificação operacional por regras determinísticas, com sinais de detecção de anomalias por Isolation Forest.”** Se mencionar aprendizado de máquina, identificar explicitamente o papel não supervisionado do Isolation Forest e suas limitações.

## Limitações metodológicas confirmadas

1. O README descreve um fluxo com “Random Forest / prob. de falha” e lista Isolation Forest + Random Forest na stack, mas o classificador não foi localizado no código atual. A documentação pública do repositório não está alinhada com o checkout inspecionado.
2. Não foi encontrado conjunto de falhas mecânicas confirmadas nem rótulo supervisionado usado por esses componentes.
3. A origem do DataFrame de treino do Isolation Forest persistido está fora do módulo; README/docstring apontam cenário normal de bancada. O tamanho e representatividade desse conjunto não foram identificados no trainer.
4. Não foi encontrada validação externa, temporal ou por máquina, nem métrica de qualidade ou monitoramento de produção para os detectores.
5. O detector por máquina treina em histórico que pode incluir situações normais e anômalas; não há rótulos para distinguir essas condições. O resultado depende do histórico disponível no processo.
6. A severidade do pipeline é decidida por thresholds e contagem de motivos. O sinal estatístico não prova causa mecânica nem risco futuro.
7. A anotação de “falha” no README não deve ser interpretada como probabilidade calibrada: não foi localizado modelo que produza essa probabilidade.

## Caminho para supervisão real

O fluxo futuro pode partir de telemetria e eventos operacionais, registrar a decisão humana e o resultado observado, definir uma taxonomia de rótulos e uma janela de previsão, revisar consistência e completude, então formar um dataset versionado. `Event` → `Decision.status` / `Decision.outcome_texto` pode ser uma semente de coleta. O texto livre não deve virar rótulo automaticamente: será necessário processo de anotação, critérios explícitos, tratamento de casos inconclusivos e vínculo temporal com máquina/componente e telemetria.

Só depois de haver volume e qualidade suficientes faz sentido treinar e avaliar um modelo supervisionado. A avaliação deve evitar vazamento temporal ou entre máquinas, reportar métricas adequadas ao custo de falsos positivos/falsos negativos e comparar com a regra de referência. Até lá, o feedback é dado potencial, não dataset validado.

## Referências auditadas

- `api_tcc/ia/deteccao_multivariada.py`
- `api_tcc/services/anomaly_detection.py`
- `api_tcc/ia/pipeline.py`
- `api_tcc/services/prescricao.py` (legado)
- `api_tcc/models.py` (`Event` e `Decision`)
- `README.md`
- `docs/limiares.md`

Esta auditoria descreve o estado encontrado em 25/09/2026. Uma revisão por pares do grupo ainda é necessária antes de tratar o documento como aceito pelo grupo; não foi registrada aprovação nesta alteração.

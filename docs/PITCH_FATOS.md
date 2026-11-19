# S12-T7 · Política de números e alinhamento factual do pitch

Status: PREPARAÇÃO FACTUAL CONCLUÍDA; REVISÃO INDEPENDENTE E ENSAIO AINDA PENDENTES

Esta matriz autoriza o que pode ser dito no palco. Número sem fonte primária,
método, unidade, data e limite não entra como fato. A pesquisa do grupo pode
orientar perguntas, mas não vira evidência por osmose. O pitch não contém
custo, preço, economia ou ROI.

Data desta auditoria local: **2026-11-19**.

## 1. Números submetidos à auditoria

| Valor ou afirmação numérica | Fonte primária (URL/documento) | Data de acesso | Estado | Uso no palco |
| --- | --- | --- | --- | --- |
| 30–40% atribuído à ANATEL em 2023 | URL ou documento primário não localizado no checkout; atribuição não confirmada | 2026-11-19 | NÃO VERIFICADO | **NÃO USAR** |
| R$ 5–15 mil por hora atribuído à Embrapa em 2022 | URL ou documento primário não localizado no checkout; atribuição não confirmada | 2026-11-19 | NÃO VERIFICADO e proibido pelo escopo do professor | **NÃO USAR** |
| 40% da frota com mais de 15 anos atribuído à ANFAVEA em 2023 | URL ou documento primário não localizado no checkout; atribuição não confirmada | 2026-11-19 | NÃO VERIFICADO | **NÃO USAR** |
| 73–85% de acurácia | Nenhum relatório primário encontrado que sustente essa faixa | 2026-11-19 | NÃO VERIFICADO | **NÃO USAR** |
| 8 cenários × 20 sementes no benchmark S5 | `docs/AVALIACAO_ANOMALIA.md`, cabeçalho do benchmark `benchmark_v1` | 2026-11-19 | VERIFICADO localmente; sintético | Usar somente para descrever o experimento |
| Precisão 0,590, recall 0,171 e F1 0,262 no cenário sintético `subida_gradual` | `docs/AVALIACAO_ANOMALIA.md`, tabela de resultados | 2026-11-19 | VERIFICADO localmente; sintético | Usar com “em cenários sintéticos” |
| Precisão 0,063 e recall 1,000 no cenário sintético `pico_isolado` | `docs/AVALIACAO_ANOMALIA.md`, tabela de resultados | 2026-11-19 | VERIFICADO localmente; sintético | Usar só para mostrar trade-off do benchmark |
| 90 mensagens no ensaio de medição de armazenamento | `docs/evidence/s6/S6-T2_REPORT.md`, “Resultado MEDIDO nesta execução” | 2026-11-19 | VERIFICADO localmente; software/bancada | Usar com contexto do ensaio |
| 81.920 B de crescimento físico e 910,22 B por mensagem | `docs/evidence/s6/S6-T2_REPORT.md`, “Resultado MEDIDO nesta execução” | 2026-11-19 | VERIFICADO localmente; SQLite em bancada | Usar com contexto; não é capacidade de hardware |
| 604.800 mensagens e 550,50 MB brutos em 14 dias | `docs/evidence/s6/S6-T2_REPORT.md`, projeção parametrizada | 2026-11-19 | Projeção, não medição de campo | **NÃO usar como capacidade física** |
| 100 mensagens na rodada oficial de resiliência | `docs/evidence/s6/S6-T5_EXECUCAO.md`, comando autorizado | 2026-11-19 | Rodada oficial não realizada | **NÃO USAR como resultado** |

### Regra de leitura

“Verificado localmente” significa que o arquivo e o resultado existem no
checkout auditado. Não significa validação de campo, eficácia mecânica,
capacidade de hardware nem resultado comercial. O número S5 é métrica de teste
sintético; S6-T2 é medição de armazenamento em software/bancada.

## 2. Claims autorizadas

| Claim | Evidência primária | Limite | Estado |
| --- | --- | --- | --- |
| O sistema ingere telemetria por HTTP e MQTT, validando e deduplicando a entrada. | `docs/CONTRATO_TELEMETRIA_V1.md` e testes de telemetria | Não prova ensaio físico em máquina | AUTORIZADA COM CONTEXTO |
| A bancada mantém outbox local, retry, ACK e prioridades A/B/C. | `docs/evidence/s8/S8-T4_S8-T5_IMPLEMENTATION.md` | Não prova outbox físico no ESP32 | AUTORIZADA COM CONTEXTO |
| O sistema registra eventos e decisões persistentes para revisão humana. | `docs/OPERATIONAL_DECISION_MEMORY.md` e testes correspondentes | Não prova correção mecânica | AUTORIZADA |
| Isolation Forest é detector não supervisionado complementar às regras de triagem. | `docs/HONESTIDADE_METODOLOGICA_ML.md` e `docs/evidence/s5/S5-T2_REPORT.md` | Não é previsão de falha, diagnóstico ou RUL | AUTORIZADA |
| A medição S6-T2 observou 81.920 B de crescimento em um ensaio de 90 mensagens. | `docs/evidence/s6/S6-T2_REPORT.md` | Medição de bancada SQLite, não de flash ou campo | AUTORIZADA COM CONTEXTO |

## 3. Abertura recomendada

> “Em uma medição de bancada, o FieldNode registrou 90 mensagens e mediu
> 81.920 B de crescimento físico no SQLite. Isso não prova uma máquina no
> campo. Prova algo mais modesto e demonstrável: a equipe mede o comportamento
> do sistema, registra a origem e deixa claro o que ainda falta validar.”

Persona para storytelling, sempre declarada como ilustrativa:

> “Persona ilustrativa: uma supervisora recebe uma leitura suspeita quando o
> uplink cai. O FieldNode não transforma isso em certeza: preserva a leitura,
> marca o contexto e deixa a decisão pendente para revisão humana.”

Não apresentar a persona como cliente, entrevista ou caso real.

## 4. Acurácia e linguagem correta

Usar:

> “No benchmark do S5, em cenários sintéticos, o resultado variou por cenário;
> por exemplo, `subida_gradual` teve precisão média de 0,590, recall médio de
> 0,171 e F1 médio de 0,262. Isso não é acurácia de campo.”

Não usar “o modelo tem 73–85% de acurácia”, “a IA prevê a falha” ou qualquer
faixa sem relatório primário, denominador e ambiente identificados. A avaliação
S5-T5 em CWRU ainda não tem tabela de resultados reais publicada em
`docs/evidence/s5/S5-T5_REPORT.md`.

## 5. O que foi removido do pitch

- Percentuais atribuídos a ANATEL, ANFAVEA ou qualquer fonte não confirmada.
- Custo horário, preço, economia e ROI.
- A faixa de acurácia 73–85%.
- Promessa de perda zero, tempo garantido ou validação em campo.
- Frase que transforme simulador, bancada ou projeção em resultado físico.

## 6. Alinhamento e critérios

| Material ou critério | Estado | Evidência ou pendência |
| --- | --- | --- |
| `README.md` | Sem os números de mercado auditados nesta tarefa | Revalidar se claim nova for adicionada |
| `docs/ROTEIRO_DEMO_BANCA.md` | Alinhado | Já orienta a não usar estatística sem fonte |
| `docs/INVESTOR_CTO_PRESSURE_TEST.md` | Atualizado nesta tarefa | Deve repetir estes limites |
| S5 | Parcialmente verificado | Métricas documentadas, sempre sintéticas |
| S6-T2 | Verificado em bancada | Medição de armazenamento documentada |
| S6-T5 | Pendente | Rodadas oficiais sem números publicados |
| Cada número factual tem linha na tabela | VERIFICADO documentalmente | Seção 1 |
| Números não verificados estão marcados como NÃO USAR | VERIFICADO documentalmente | Quatro alegações externas e acurácia |
| Finanças estão fora | VERIFICADO documentalmente | Seção 5 |
| Persona é ilustrativa | VERIFICADO documentalmente | Seção 3 |
| Revisão por pessoa que não escreveu o pitch | PENDENTE | Registrar nome, data, achados e correções |
| Ensaio externo e gravação | PENDENTE | Não há ata ou gravação no checkout |

Até a revisão independente, o status correto é **preparado para revisão**, não
“pronto para palco”. A honestidade aqui é o detector de fumaça contra uma
pergunta simples com potencial de incendiar a apresentação.

# S5-T4 - Plano de coleta de dataset rotulado real

**Semana:** 5 - Honestidade de ML: separar regra de predição real  
**ID:** S5-T4  
**Natureza:** planejamento metodológico  
**Dependências:** S4-T2 e S4-T3  
**Implementação nesta etapa:** `DEFER`  
**Pré-requisito:** acúmulo natural de decisões com desfecho observável durante o uso e as demonstrações

## 1. Objetivo

Definir como o FieldNode poderá, no futuro, transformar registros operacionais em um dataset supervisionado para manutenção ou risco de falha. O objetivo desta tarefa é desenhar o protocolo de coleta e revisão, não criar o dataset nem treinar um modelo.

Hoje o sistema possui sinais de telemetria, `Event` e `Decision`, mas ainda não possui quantidade suficiente de casos com desfecho humano e observação posterior para sustentar a afirmação de que existe um modelo preditivo real. O histórico de `Decision.status` e `Decision.outcome_texto` é matéria-prima potencial, não um dataset pronto.

O problema a resolver é:

```text
telemetria -> Event -> Decision -> ação/feedback -> desfecho observado -> rótulo revisado
```

O plano deve quebrar o ciclo frágil em que as próprias regras produzem os rótulos que depois parecem validar o modelo.

## 2. Arquitetura real considerada

No checkout atual:

- `Event` pertence a uma `Machine`, pode apontar para a `LeituraTelemetria` de origem e registra `tipo`, `severidade`, `status`, contexto e horário de criação.
- `Decision` pertence a uma `Machine`, pode apontar para o `Event` que motivou a recomendação e registra texto, ação recomendada, severidade, confiança, status, horários, autor e `outcome_texto`.
- Os status existentes de `Decision` são `PENDENTE`, `APROVADA`, `REJEITADA`, `EXECUTADA` e `EXPIRADA`.
- Não existe atualmente um status `IGNORADA`; ele não deve ser inventado para preencher o protocolo.

O vínculo conceitual necessário é:

```text
LeituraTelemetria
        |
        v
      Event ----> Decision ----> outcome_texto / observação posterior
        |             |
        +-------------+---------> futuro rótulo revisado
```

O rótulo não será copiado automaticamente de nenhum campo. Cada exemplo deverá manter a origem, a regra aplicada, a evidência observada e a decisão de revisão.

## 3. Princípio central: rótulo fraco, não causalidade

O protocolo é de **weak supervision**. Ele usa sinais observáveis e feedback operacional para produzir candidatos a rótulo, mas não prova que uma decisão causou ou evitou uma falha.

Em particular:

- `EXECUTADA` não significa automaticamente sucesso.
- `REJEITADA` não significa automaticamente falha.
- `outcome_texto` não é um rótulo automático; é evidência qualitativa que precisa ser interpretada por critérios definidos e revisão humana.
- ausência de `Event` não é prova de que a máquina ficou saudável.
- correlação entre ação e evento posterior não é evidência de causalidade.

A linguagem permitida enquanto o protocolo não for implementado deve ser: o FieldNode coleta feedback operacional para futuramente construir um dataset supervisionado real. Não se deve afirmar que o sistema já prevê falhas de manutenção.

## 4. Unidade de amostra

Cada `Decision` elegível corresponde a **uma unidade primária de rotulagem**. Eventos posteriores serão evidências do desfecho dessa unidade, não novos exemplos independentes.

Isso evita contar várias ocorrências do mesmo episódio como se fossem observações diferentes e inflar artificialmente o dataset.

Uma decisão só pode ser elegível quando houver:

1. máquina identificável;
2. timestamp consistente;
3. vínculo com `Event`, quando o evento de origem existir;
4. ação e contexto suficientes para saber o que foi recomendado;
5. status operacional registrando o que ocorreu;
6. janela de observação encerrada;
7. qualidade mínima de telemetria para interpretar a ausência ou presença de eventos.

## 5. Protocolo de rotulagem futura

Para cada decisão, o processo deverá preservar:

1. o `Event` de origem e sua natureza;
2. a `Decision` e seu status no momento do desfecho;
3. o conteúdo de `outcome_texto`, quando preenchido;
4. os eventos posteriores da mesma máquina e natureza;
5. a janela observada e a qualidade dos dados;
6. a justificativa do rótulo;
7. a revisão e a versão do protocolo utilizadas.

O rótulo futuro deve ser estruturado, por exemplo:

| Categoria | Interpretação operacional | Uso inicial |
| --- | --- | --- |
| `RISCO_OBSERVADO` | evento crítico similar ocorreu na janela | candidato a classe positiva (`1`) |
| `SEM_EVENTO_OBSERVADO` | decisão executada e nenhum evento similar foi observado na janela válida | candidato a classe negativa (`0`) |
| `INDETERMINADO` | evidência insuficiente, contraditória ou incomparável | excluir do treino inicial |

Os nomes são categorias de protocolo, não campos a serem criados agora.

## 6. Candidatos a rótulo positivo

Uma `Decision` poderá ser candidata a `RISCO_OBSERVADO` quando:

- estiver associada a uma máquina e a uma recomendação rastreável;
- a decisão tiver sido `REJEITADA` ou tiver expirado sem execução registrada, conforme revisão do grupo;
- um `Event` crítico similar ocorrer depois da decisão e dentro da janela válida;
- a similaridade não depender apenas da proximidade temporal;
- não houver evidência de que o evento posterior é duplicata ou parte do mesmo episódio já usado como origem.

O caso positivo significa apenas que houve risco ou evento compatível observado após uma ação não executada. Não significa que a rejeição causou a ocorrência.

Se uma decisão `EXECUTADA` for seguida por evento similar, o caso também deverá ser revisado, mas não deve ser forçado para uma interpretação causal. Pode ser `RISCO_OBSERVADO`, `INDETERMINADO` ou outra categoria definida antes do congelamento do dataset, conforme a natureza da ação e a evidência disponível.

## 7. Candidatos a rótulo negativo

Uma `Decision` `EXECUTADA` poderá ser candidata a `SEM_EVENTO_OBSERVADO` quando:

- a execução estiver registrada de forma verificável;
- a janela de observação estiver completa;
- não houver `Event` crítico similar da mesma máquina durante a janela;
- a telemetria e o estado de coleta forem suficientes para considerar a ausência informativa;
- `outcome_texto`, quando existente, não contradizer a classificação.

Esse rótulo significa **ausência de evento similar observado após uma decisão executada**. Não significa que a ação preveniu a falha. O contrafactual, isto é, o que teria acontecido sem a ação, não é observado diretamente.

Uma decisão rejeitada, expirada ou sem execução que não seja seguida por evento não deve virar automaticamente rótulo negativo. Sem intervenção registrada, a ausência de evento tem interpretação limitada.

## 8. Casos indeterminados e exclusões

Devem permanecer como `INDETERMINADO` ou ser excluídos da primeira rodada:

- decisão sem máquina ou vínculo temporal confiável;
- decisão sem janela completa;
- `outcome_texto` contraditório ou impossível de interpretar;
- evento posterior de natureza diferente;
- manutenção realizada por motivo não relacionado ao alerta;
- dúvida sobre execução real da ação;
- dados atrasados, offline ou ausentes que impeçam interpretar a janela;
- duplicidade ou vários eventos do mesmo episódio;
- troca de identidade da máquina;
- inconsistência de timestamp;
- qualidade de dados comprometida durante parte relevante da janela;
- qualquer caso em que não seja possível explicar por que o rótulo foi atribuído.

Não forçar casos ambíguos para `0` ou `1`. Um dataset menor e auditável vale mais que uma contagem bonita com certezas de papelão.

## 9. Definição de evento similar

Para evitar tratar qualquer evento posterior como confirmação, a similaridade deverá considerar, nesta ordem:

1. mesma máquina;
2. mesmo `Event.tipo`, quando aplicável;
3. mesma família de sinal ou componente, se essa informação existir no contexto persistido;
4. severidade compatível;
5. compatibilidade operacional revisada pelo grupo.

Os tipos disponíveis no modelo incluem `TEMP_ALTA`, `VIBRACAO_ALTA`, `ANOMALIA_ML`, `ANOMALIA_ESTATISTICA` e `TENDENCIA_RISCO`. Não se deve inventar uma granularidade de componente que o sistema atual não registra. Se o contexto não permitir decidir a similaridade, o caso será indeterminado até que o protocolo seja complementado.

## 10. Janela de observação

Como proposta operacional inicial, usar uma janela de **30 dias corridos** após o instante da `Decision`, ou após o instante de execução quando esse momento estiver disponível.

Essa janela não é uma verdade científica. Ela é um ponto de partida para tornar a coleta consistente, escolhido por ser longo o bastante para observar manutenção operacional em muitos ciclos e curto o bastante para evitar misturar episódios muito distantes.

O grupo deverá revisar a janela antes de congelar o primeiro dataset. Caso tipos de evento tenham horizontes claramente diferentes, a versão futura do protocolo poderá definir janelas por tipo. A definição escolhida deve permanecer fixa durante uma rodada de coleta e treinamento.

Uma janela só é encerrada quando:

- transcorrer o período definido; e
- houver dados suficientes para afirmar que a ausência de evento não é apenas falha de coleta.

## 11. Dados atrasados, offline e qualidade

`stale` não significa automaticamente inválido, mas também não pode ser tratado como observação em tempo real. O protocolo deverá registrar se houve atraso, perda de conectividade ou reprocessamento durante a janela.

O `trust_score` e `MachineDataHealth` podem ser usados futuramente como critérios de qualidade, feature ou análise de sensibilidade. Eles não devem ser usados automaticamente como rótulo. Se a qualidade da máquina estiver comprometida a ponto de esconder eventos, o caso será `INDETERMINADO`, não negativo.

## 12. Prevenção de vazamento de informação

As features de um exemplo devem estar limitadas ao que estava disponível no instante da decisão, incluindo telemetria anterior, contexto do `Event` de origem e metadados conhecidos naquele momento.

Não podem entrar como feature:

- eventos posteriores à decisão;
- `outcome_texto` registrado depois da decisão;
- status final ou rótulo revisado;
- qualquer manutenção ocorrida dentro da janela;
- estatísticas calculadas usando o futuro;
- dados de teste ou de decisões posteriores ao período de treino.

Eventos posteriores servem exclusivamente para construir o desfecho durante a rotulagem. Misturar desfecho com entrada faria o modelo responder depois da prova, o que é uma forma elegante de trapacear e uma forma péssima de operar.

## 13. Censura temporal

Decisões recentes cuja janela ainda não terminou são casos censurados. Elas não devem ser contadas como `SEM_EVENTO_OBSERVADO` apenas porque, até hoje, nenhum evento foi registrado.

Também há censura quando o sistema perde observabilidade da máquina, quando a coleta é interrompida ou quando os dados chegam atrasados sem reconstrução confiável. Esses casos permanecem pendentes ou indeterminados até haver evidência suficiente.

## 14. Gate de entrada para implementação

A implementação da coleta automática e do primeiro treino só poderá ser revisitada quando todos estes critérios forem avaliados:

- pelo menos **200 `Decision` elegíveis** com outcome ou desfecho observável;
- janelas de observação encerradas;
- labels estruturáveis e revisados;
- distribuição de classes conhecida;
- diversidade mínima de máquinas;
- diversidade mínima de tipos de `Event`;
- período de coleta suficientemente amplo;
- qualidade mínima de dados avaliada;
- protocolo de similaridade aprovado;
- processo de revisão e resolução de divergências definido;
- protocolo de rotulagem congelado para a rodada.

O número 200 é um mínimo operacional inicial para decidir se vale investigar o treinamento. Não é garantia estatística universal, nem autorização para treinar automaticamente.

## 15. Auditoria de qualidade antes do treino

Ao atingir o gate, primeiro produzir uma análise do conjunto:

```text
N total de Decisions elegíveis
N positivos
N negativos
N indeterminados
N por máquina
N por tipo de Event
N por período
N por status da Decision
N por qualidade dos dados
```

O grupo deverá revisar uma amostra dos rótulos, procurar divergências e verificar se uma máquina ou tipo de evento domina o conjunto. Se a distribuição for insuficiente, enviesada ou impossível de explicar, o treino deve continuar adiado.

## 16. Processo de treino e avaliação futuro

O primeiro experimento deverá usar divisão temporal, por exemplo:

```text
período histórico inicial -> treino
período posterior         -> teste
```

Não misturar aleatoriamente decisões do futuro no treino. A unidade de avaliação continua sendo a `Decision`, respeitando dependências entre episódios da mesma máquina.

Antes de qualquer modelo supervisionado, estabelecer uma baseline operacional, preferencialmente a regra atual de risco/anomalia. Um candidato só poderá ser considerado avanço se superar a baseline em dados de teste que não participaram do treino.

As métricas serão escolhidas conforme o objetivo e a distribuição final, incluindo quando fizer sentido `precision`, `recall`, `F1`, matriz de confusão e PR-AUC/ROC-AUC. O custo operacional de falsos positivos e falsos negativos deverá ser explicitado; não existe métrica mágica que dispense decisão de negócio.

O modelo futuro deverá ser reproduzível e versionado, com registro de dataset, protocolo, features, split, parâmetros, métricas e artefato gerado.

## 17. Governança e rastreabilidade

Antes do primeiro treinamento, o grupo deverá definir:

- quem pode revisar rótulos;
- quem resolve divergências;
- quem aprova uma versão do dataset;
- como correções de rótulo são registradas;
- quando a coleta é congelada;
- como o caminho `Event -> Decision -> outcome -> label` é auditado.

O texto livre de `outcome_texto` deve permanecer como evidência humana. Não implementar agora NLP, LLM, análise de sentimento ou classificação automática desse texto.

## 18. Limitações metodológicas

Mesmo com 200 decisões, o dataset poderá sofrer com:

- viés de seleção, pois só entram casos observados pelo sistema;
- viés de intervenção, pois operadores agem quando percebem maior risco;
- confundimento por manutenção realizada por outro motivo;
- feedback incompleto;
- contrafactual ausente;
- mudança de comportamento após a adoção do FieldNode;
- drift de máquinas, sensores e operação;
- desbalanceamento entre falhas e não-falhas;
- diferenças de qualidade entre máquinas e períodos.

Essas limitações não anulam o plano. Elas impedem que um rótulo fraco seja vendido como verdade causal e devem aparecer na avaliação do primeiro modelo.

## 19. Implementação adiada (`DEFER`)

Nesta etapa não serão criados:

- tabela de labels, dataset ou exemplos de treino;
- migration;
- management command de coleta;
- exportador automático;
- notebook ou pipeline de treinamento supervisionado;
- endpoint ou tarefa assíncrona;
- alteração em `Event`, `Decision`, frontend, hardware ou regras de IA atuais.

A implementação fica classificada como `DEFER` e será revisitada inicialmente em **S9**, ou antes/depois se os dados atingirem o gate com evidência suficiente.

## 20. Definition of Done do S5-T4

- [x] protocolo documental criado em `docs/PLANO_DATASET_ROTULADO.md`;
- [x] relação `Event -> Decision -> outcome -> label` descrita;
- [x] status real de `Decision` respeitado, sem inventar `IGNORADA`;
- [x] `outcome_texto` tratado como evidência, não como label automático;
- [x] candidatos positivos, negativos e indeterminados definidos;
- [x] janela inicial de 30 dias proposta e marcada como revisável;
- [x] censura temporal, dados offline e qualidade considerados;
- [x] regra de prevenção de leakage e discussão do contrafactual incluídas;
- [x] gate de pelo menos 200 decisões elegíveis definido;
- [x] diversidade, auditoria, split temporal, baseline e métricas futuras definidos;
- [x] implementação explicitamente marcada como `DEFER`;
- [x] nenhuma alteração de código, banco ou dependência necessária nesta semana.

**Critério central:** não fabricar um dataset para justificar um modelo. Esperar que os dados operacionais produzam evidência suficiente para justificar, ou não, um modelo supervisionado.

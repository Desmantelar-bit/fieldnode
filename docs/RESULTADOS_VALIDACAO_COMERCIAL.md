# Resultados de validação comercial

## Status da consolidação

Este documento consolida o que está efetivamente registrado no repositório até
09/10/2026. Ele é um relatório de descoberta qualitativa, não uma prova
estatística de mercado nem uma confirmação de venda.

| Critério | Estado | Evidência disponível |
|---|---|---|
| Registros comerciais investigados | VERIFICADO | Relatório histórico anterior e roteiro S9-T4 localizados no repositório. |
| Registros históricos conciliados | VERIFICADO | Três entradas, todas datadas de 19/09/2026 e atribuídas a contextos distintos. |
| Entrevistas com evidência primária anexada | NÃO VERIFICADO | Não há ficha preenchida, transcrição, gravação, convite, agendamento ou ata correspondente no repositório. |
| Entrevistas concluídas e verificáveis | 0 confirmadas | Os três registros são tratados abaixo como históricos parciais, não como entrevistas plenamente auditáveis. |
| Meta de 5–6 conversas | NÃO ATINGIDA | Não existem registros adicionais de conversas 4–6. |
| Pelo menos três perfis operacionais | NÃO ATINGIDO | Os registros disponíveis são de especialistas técnicos ligados a fabricantes/plataforma; não há gestor de frota, manutenção, supervisor de colheita, operador ou analista de usina com ficha verificável. |
| Disposição concreta de pagar | NÃO EVIDENCIADA | Não há orçamento, processo de compra, proposta, piloto autorizado ou compromisso comercial documentado. |

A meta de 5–6 conversas continua pendente. Não será preenchida com pesquisa
secundária, demonstração técnica ou entrevistas imaginárias. Estatística de
guardanapo não vira evidência só porque foi colocada numa tabela bonita.

## 1. Escopo e metodologia

O objetivo era investigar processos reais de operação, manutenção, dados,
alertas, impactos, alternativas e critérios de compra, além de testar a tese
de valor de uma solução complementar para frotas de marcas diferentes.

Foram examinados:

- `docs/RESULTADOS_VALIDACAO_COMERCIAL.md`, versão histórica anterior;
- `docs/ROTEIRO_VALIDACAO_COMERCIAL.md`, elaborado para S9-T4;
- referências comerciais em `docs/SEGURANCA.md`, `docs/faq_banca.md` e demais
  documentos do repositório;
- histórico Git do relatório e dos documentos relacionados;
- arquivos do repositório em busca de fichas, convites, contatos, agendamentos,
  atas e registros de recrutamento.

O roteiro S9-T4 recomenda começar pelo processo atual e por episódios concretos,
separando relato, evidência apresentada, interpretação, hipótese, contradição e
desconhecido. Os três registros históricos foram produzidos antes desse roteiro
e não podem ser reescritos retroativamente como se o tivessem seguido.

Não há método de recrutamento, duração, consentimento, perguntas efetivamente
realizadas ou fonte primária documentados para os três registros. Também não há
canal de comunicação autorizado, destinatário identificado ou agendamento
registrado para entrevistas adicionais nos arquivos examinados. Portanto, a
busca adicional fica pendente de uma ação humana de recrutamento com autorização
e registro adequado.

## 2. Inventário consolidado

| ID | Data/período | Perfil registrado | Estado do registro | Dor relatada no resumo | Sinal de pagamento | Limitação principal |
|---|---|---|---|---|---|---|
| INT-01 | 19/09/2026 | Especialista técnico, John Deere Brasil | Registro histórico parcial; conversa alegada, sem fonte primária anexada | Conectividade offline, frota legada e ausência de visão local durante o período sem rede | Nível 0, sem evidência de pagamento | Não há orçamento, processo de compra ou integração autorizada documentados. |
| INT-02 | 19/09/2026 | Especialista técnico, Solinftec | Registro histórico parcial; conversa alegada, sem fonte primária anexada | Limite da cobertura mesh, necessidade de análise local e preocupação com duplicação na sincronização | Nível 0, sem evidência de pagamento | O valor de hardware citado é critério relatado, não compromisso de compra. |
| INT-03 | 19/09/2026 | Especialista técnico, Case IH Brasil | Registro histórico parcial; conversa alegada, sem fonte primária anexada | Componentes sem cobertura do barramento, máquinas legadas, exportação e segurança no upload | Nível 0, sem evidência de pagamento | Não há comprovação de contato acionável com usina ou concessionária. |

### Contagem sem duplicação

Há três registros históricos com empresas/contextos distintos. Como a fonte
primária não está disponível, a contagem auditável de entrevistas concluídas é
zero. A contagem histórica registrada é três. Essas duas contagens não devem ser
misturadas.

## 3. Análise dos registros históricos

### INT-01, contexto John Deere

O resumo histórico relata uso do John Deere Operations Center e transmissão
dependente de conectividade. Registra como problemas a perda de visibilidade em
áreas sem cobertura, máquinas antigas sem acesso ao barramento CAN/J1939 e a
necessidade de sincronizar dados acumulados quando o sinal retorna. Também
registra um valor de impacto de R$ 5.000 a R$ 15.000 por hora de parada e a
preferência relatada por uma indicação local de risco.

Esses pontos são relatos preservados de um documento anterior, não métricas
independentemente verificadas neste ciclo. O documento não informa perguntas,
respostas literais, método de medição, duração ou autorização para uma etapa
seguinte. Não há evidência de orçamento, compra, piloto aprovado ou integração
com o JDOC.

Classificação: sinal exploratório, força baixa para generalização de mercado.

### INT-02, contexto Solinftec

O resumo histórico relata dependência de infraestrutura de rádio/mesh em parte
das operações, perda de visibilidade fora da cobertura e interesse relatado em
processamento local com classificação NORMAL, ATENÇÃO ou CRÍTICO. Também registra
preocupação com duplicação de pacotes e UUID durante a ressincronização, além de
um limite de hardware abaixo de R$ 500 por máquina.

O limite de custo é um critério relatado no resumo, não uma cotação, orçamento ou
disposição de pagar. Não há fonte primária para verificar contexto, autoria,
perguntas ou autorização de continuidade. Também não há comprovação de
compatibilidade com a infraestrutura Solinftec.

Classificação: sinal exploratório, força baixa para generalização de mercado.

### INT-03, contexto Case IH

O resumo histórico relata limitações de visibilidade remota em máquinas legadas,
componentes que não aparecem no barramento, demanda por dados brutos para
processos de BI e preocupação com segurança do upload após períodos offline.
Também registra a necessidade de considerar frotas mistas e sensores externos.

O caso de uma usina em Araçatuba/Clealco aparece como contexto mencionado no
resumo. Isso não comprova uma conversa com a usina, uma autorização de contato,
uma integração ou uma demanda representativa de outras usinas. Não há registro
de orçamento, piloto aprovado ou processo de compra.

Classificação: sinal exploratório, força baixa para generalização de mercado.

## 4. Níveis de disposição de pagamento

Critério usado nesta consolidação:

- **Nível 0, sem evidência:** pagamento não investigado ou sem registro suficiente;
- **Nível 1, interesse verbal:** interesse declarado sem critério econômico concreto;
- **Nível 2, processo de compra identificado:** orçamento, aprovador, critérios ou condições econômicas documentados;
- **Nível 3, compromisso concreto:** avaliação técnica autorizada, piloto formal, processo de aquisição ou negociação real documentada.

Os três registros ficam no Nível 0. Há referências a custos de parada, teto de
hardware e critérios técnicos de piloto, mas nenhum desses itens prova que uma
organização esteja disposta a pagar pelo FieldNode. Não há evidência suficiente
nem para atribuir Nível 1 com segurança.

## 5. Matriz das hipóteses comerciais

| Hipótese | Evidência favorável nos registros | Evidência contrária ou lacuna | Perfis e n | Qualidade | Conclusão provisória | Próximo teste |
|---|---|---|---|---|---|---|
| H1. Dados atrasados ou fragmentados prejudicam decisões | Os três resumos relatam perda de visibilidade fora de celular, mesh ou Wi-Fi. | Sem fonte primária, episódio operacional e frequência verificáveis. | Especialistas técnicos; 3 registros históricos, 0 entrevistas auditáveis | Baixa | Parcialmente apoiada como hipótese exploratória | Entrevistar gestor de frota e supervisor sobre um caso recente e tempo até a ação. |
| H2. Dados de marcas diferentes são uma dor relevante | INT-01 e INT-03 mencionam frotas legadas/mistas e INT-03 menciona exportação para BI. | Não há usuários finais nem medida de retrabalho, atraso ou custo de integração. | Especialistas técnicos; 2 registros históricos relevantes | Baixa | Parcialmente apoiada | Entrevistar operação multi-marca e tecnologia da usina separadamente. |
| H3. Painel unificado agrega valor sobre ferramentas existentes | Os resumos mencionam pontos cegos e múltiplas plataformas. | Não há comparação de decisão, uso contínuo, preferência por painel ou autorização de piloto. | Especialistas técnicos; n não verificável | Baixa | Inconclusiva | Perguntar quando uma fonte adicional mudaria uma decisão e quando não valeria o custo. |
| H4. Confiabilidade dos alertas determina adoção | Há preocupação relatada com classificação local, sincronização e segurança. | Não há teste de precisão, falso positivo, falso negativo ou critério de confiança. | Especialistas técnicos; n não verificável | Baixa | Inconclusiva | Investigar alertas ignorados, evidência necessária e consequências de erro. |
| H5. Paradas têm impacto que justifica solução de apoio | Os resumos citam R$ 5.000–15.000/hora e risco de incêndio. | Valores não têm fonte de medição anexada; não há comprador ou orçamento vinculado. | Especialistas técnicos; 3 registros históricos | Baixa | Parcialmente apoiada como relato, não como prova econômica | Solicitar episódio recente, unidade de medida, registro e decisão tomada. |
| H6. Existe disposição concreta de pagar | Nenhuma evidência documental de compra, orçamento ou compromisso. | Nível 0 para os três registros. | n=0 com sinal de pagamento verificável | Não evidenciada | Não investigada de forma suficiente | Mapear orçamento, aprovador e próximo passo autorizado com usuários compradores. |
| H7. Existem condições para acessar os dados necessários | São citados JDOC, Alice, AFS Connect, sensores externos e exportação. | Não há autorização, contrato, API aprovada, permissões ou teste em equipamento físico. | Especialistas técnicos; n não verificável | Baixa | Inconclusiva | Entrevistar tecnologia sobre permissões, formatos, contratos e requisitos de segurança. |
| H8. Recomendação baseada em dados seria aceita no fluxo real | Há relatos de valor para alertas locais e classificação de risco. | Não há observação de fluxo real, responsável operacional ou decisão efetivamente tomada. | Especialistas técnicos; n não verificável | Baixa | Inconclusiva | Observar ou reconstruir com supervisor/manutenção uma decisão real, sem apresentar solução antes. |

“Parcialmente apoiada” aqui significa apenas que os registros contêm sinais
compatíveis com a hipótese. Não significa validação de mercado.

## 6. Dor principal: resultado provisório

O tema que aparece com maior consistência nos três resumos é a disponibilidade
de dados durante períodos sem conectividade, acompanhada por alertas locais e
sincronização posterior. Isso aponta mais diretamente para a categoria **E,
disponibilidade e qualidade dos dados**, com relação às categorias **B,
confiabilidade de alertas**, e **A, integração multi-marca**.

Não é metodologicamente defensável declarar integração multi-marca como dor
dominante. A amostra é pequena, concentrada em especialistas técnicos, sem
entrevistas auditáveis com quem opera, mantém ou compra. O resultado correto é:

> categoria mais recorrente nos registros históricos: disponibilidade de dados
> offline; dor dominante de mercado: inconclusiva.

## 7. Concorrentes, sistemas e alternativas

John Deere Operations Center, Alice/Solinftec e AFS Connect/Case IH aparecem
como sistemas ou contextos atribuídos aos registros históricos. A simples
menção não prova insatisfação, inferioridade, intenção de substituição ou espaço
comercial para o FieldNode.

O material disponível sugere uma hipótese de coexistência ou complementação em
cenários offline, legados e multi-marca. Não comprova que os fabricantes ou
usinas aceitariam uma integração, nem que o FieldNode deveria substituir
plataformas nativas.

## 8. Limitações e pendências de coleta

- três registros históricos no documento anterior, todos do mesmo período;
- nenhuma ficha, transcrição, gravação ou evidência primária anexada;
- ausência de gestor de frota, manutenção, supervisor de colheita, operador e
  analista de tecnologia da usina com registro verificável;
- método de recrutamento, taxa de resposta, duração e consentimento não
  registrados;
- ausência de contato acionável e de autorização documentada para novas
  abordagens;
- ausência de evidência de orçamento, piloto, compra ou compromisso comercial;
- dependência de relatos sem verificação independente;
- impossibilidade de generalizar para usinas, fabricantes ou mercado;
- impossibilidade de estimar mercado, conversão, receita ou disposição de pagar;
- diferenças entre o roteiro histórico e o roteiro S9-T4;
- o caso de usina em MS/Araçatuba permanece contexto a investigar, não entrevista
  adicional nem prova de mercado.

## 9. Recomendações para a Semana 10

1. Manter disponibilidade de dados offline como hipótese de trabalho, sem
   apresentá-la como dor de mercado confirmada.
2. Priorizar três entrevistas auditáveis com perfis diferentes: gestor de frota,
   responsável por manutenção e supervisor de frente de colheita. Depois buscar
   operador e tecnologia da usina para completar o contraste.
3. Usar o roteiro S9-T4 sem apresentar o FieldNode antes de entender o processo
   atual. Registrar episódio, frequência, impacto, fonte da métrica, alternativas
   e casos contrários.
4. Investigar compra separadamente: orçamento, aprovador, critério de piloto,
   etapa autorizada e condição que faria a organização interromper o teste.
5. Tratar integração multi-marca como hipótese aberta. Só priorizá-la acima de
   confiabilidade de alertas, manutenção ou qualidade dos dados depois de ouvir
   usuários diretamente afetados.
6. Não usar demonstração técnica, suporte a dois fabricantes simulados,
   execução de LLM ou teste do dashboard como substituto de validação comercial.

## 10. Definition of Done desta consolidação

- [x] Histórico comercial disponível no repositório investigado.
- [x] Três registros antigos conciliados sem duplicação aparente.
- [x] Registros históricos separados de entrevistas verificáveis.
- [x] Hipóteses, dor provisória, pagamento e limitações consolidados.
- [x] Ausência de contatos e de entrevistas adicionais registrada sem exposição de dados pessoais.
- [x] Meta de 5–6 conversas marcada como não atingida.
- [ ] Cinco ou seis conversas reais documentadas e classificadas.
- [ ] Pelo menos três perfis operacionais representados por entrevistas verificáveis.
- [ ] Evidência de processo de compra, piloto autorizado ou disposição concreta de pagar.

## 11. Separação das evidências técnicas

Testes de autenticação, isolamento de `DEMO_MODE`, endpoints, dashboard, IA,
telemetria e exportação pertencem à validação técnica do produto. Eles não foram
usados para aumentar a contagem de entrevistas nem para inferir disposição de
pagamento. As evidências técnicas continuam nos documentos e testes próprios do
repositório.

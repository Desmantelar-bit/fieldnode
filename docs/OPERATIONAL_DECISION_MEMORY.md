# Operational Decision Memory

## Arquitetura consolidada

`Event` registra uma ocorrência operacional derivada de telemetria, com máquina,
leitura de origem, severidade, qualidade da evidência, prioridade heurística e
estado aberto/fechado. `Decision` é a única entidade ativa que representa uma
recomendação operacional.

```text
telemetria -> validação/idempotência -> Event -> Decision -> aprovação humana
                                      \-> AuditLog
```

O serviço `api_tcc.services.decisions` é o caminho central de criação e de
transição de Decisions. O pipeline de análise produz uma análise; ele não cria
uma entidade paralela. A persistência passa por `persistir_decision_da_analise`
ou pelo caminho de anomalia do mesmo serviço.

Evidências permanecem associadas ao `Event` e à leitura de origem. A origem do
dado continua explícita na telemetria; resultados simulados não são descritos
como medições físicas. Confiança nula continua sendo nula quando o pipeline não
produz um score próprio.

## Compatibilidade e histórico

As rotas `/api/prescricoes/`, `/api/prescricoes/lista/` e
`/api/prescricoes/<maquina_id>/` continuam disponíveis como camada de
compatibilidade e retornam dados derivados de `Decision`, com `Deprecation: true`.
Elas não consultam nem persistem a entidade antiga.

A migration `0041_migrate_prescricao_to_decision` converte registros históricos
antes de remover a tabela legada. O mapeamento preserva texto, título, status,
data e identificador original em `Decision.detalhes`; registros sem Event
mantêm `event=null`, porque fabricar uma ocorrência seria falsificar o histórico.

## Limites atuais

Feedback de limiar e integrações nativas com agendas externas continuam fora
do escopo. O resultado informado pelo operador continua sendo relato, não prova
de eficácia física.
## S4-T4 e S4-T5

`WorkOrder` é criada pela aprovação humana da `Decision`. A OS pode sair em `.ics`, JSON ou mensagem pronta; o WhatsApp só recebe um link gerado para revisão humana. Webhook é explícito, assinado com HMAC e limitado a três tentativas; falha persistente vai para `DeadLetterEntry(contexto=WEBHOOK)`.

Ao registrar a execução, a OS recebe `concluida_em`. O comando `reavaliar_decisoes` compara leituras válidas dentro da política explícita de `OrganizationPolicy.reevaluation_policy` e registra `Reevaluation`. Sem regra, janela ou qualidade temporal suficientes, o resultado é `DADOS_INSUFICIENTES`. `outcome_texto` permanece relato informado e não é promovido a prova de eficácia física.

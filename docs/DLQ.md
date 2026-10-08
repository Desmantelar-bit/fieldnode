# Dead Letter Queue de telemetria

`DeadLetterEntry` é um registro persistente para inspeção de falhas inesperadas
em etapas do processamento. Não é uma fila de execução e não substitui
`TelemetriaInvalida`, que registra o fluxo normal de payload rejeitado pela
validação.

## Cobertura atual

Há captura DLQ implementada para:

- falhas inesperadas durante a geração/persistência de Event em
	`avaliar_leitura()`;
- falhas inesperadas durante o processamento e a persistência de Decision em
	`persistir_decision_da_analise()`.

Essa lista não representa cobertura total do sistema. Qualquer outra etapa que
não tenha captura DLQ explícita permanece fora da cobertura, incluindo outros
caminhos de criação de Event/Decision, processamento MQTT, sincronização,
análises e etapas laterais da ingestão. A presença de um contexto no enum não
significa que todos os caminhos daquela categoria estejam instrumentados.

## Contextos

- `VALIDACAO`: reservado a falhas inesperadas na etapa de validação/ingestão;
	não representa o fluxo normal de payload inválido, que é registrado em
	`TelemetriaInvalida`. Observação: a captura genérica atual de
	`registrar_leitura()` também usa esse contexto como fallback quando uma falha
	inesperada não traz um contexto mais específico; portanto, o valor não prova
	sozinho que a falha ocorreu estritamente durante a validação.
- `EVENTO`: falha inesperada na geração/persistência de Event. A captura ativa
	descrita acima ocorre em `avaliar_leitura()`.
- `DECISAO`: falha inesperada na geração/persistência de Decision. A captura
	ativa descrita acima ocorre em `persistir_decision_da_analise()`.
- `SYNC`: reservado para futura integração/sincronização; atualmente não há
	caminho ativo de captura para esse contexto.

## Comportamento e limites

A DLQ persiste evidência para inspeção autenticada em `GET /api/dlq/`. Ela não
faz retry automático e não implementa reprocessamento automático. As entradas
começam com `tentativas=1` e `resolvido=false`; não há workflow automático de
resolução.

`registrar_leitura()` preserva seu contrato existente de retorno controlado:
`("criado", id)`, `("duplicata", id)`, `("invalido", motivo)` ou
`("erro", detalhe)`. No caminho de ingestão, uma falha inesperada pode ser
registrada na DLQ após o rollback e convertida em resultado `"erro"`; não se
afirma que toda exceção seja relançada até o chamador da ingestão. Os serviços
`avaliar_leitura()` e `persistir_decision_da_analise()` registram a falha e
relançam a exceção quando chamados diretamente.

Celery e RabbitMQ permanecem **DEFER**: não fazem parte do escopo deste bloco e
não há fila externa necessária para a DLQ atual.

`payload_referencia` guarda somente identificadores pequenos e serializáveis,
como `leitura_id`, `device_id`, `message_id`, `sequence_number` ou
`maquina_id`. Payload bruto, credenciais e traceback não são persistidos.

Como a DLQ usa o mesmo banco da aplicação, uma indisponibilidade do banco pode
impedir o registro da evidência. Nesse caso, a falha de persistência da DLQ é
enviada ao log e não deve mascarar a exceção original.

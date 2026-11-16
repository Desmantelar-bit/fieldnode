# S6-T4 - reconstrução temporal incremental

## Implementação

`api_tcc/services/reconstrucao.py` ordena por `timestamp` (`event_time`), usa
`recebido_em` somente para auditoria e recalcula Trust Score na vizinhança de
cinco minutos da leitura tardia, com até `HISTORY_LIMIT` leituras anteriores
como contexto. O selo `LeituraTelemetria.atrasado` não representa falha
mecânica. Leituras `unsynced` não recebem atraso inventado.

Eventos derivados carregam o selo `Event.atrasado`; decisões fechadas não são
reabertas pelo serviço. A idempotência da ingestão continua sendo
`(device_id, message_id)`.

## Evidência executada

```powershell
venv\Scripts\python.exe manage.py test api_tcc.tests.test_reconstrucao api_tcc.tests.test_telemetria --verbosity 0
```

Resultado observado: `Ran 29 tests ... OK`, incluindo leitura recebida seis
horas depois, ordenação por `timestamp`, preservação de `recebido_em`, selo de
atraso e reexecução sem duplicata.

## Limites

O recálculo atual atualiza o Trust Score individual da janela. A consolidação
histórica de `MachineDataHealth` e a reconciliação completa de gaps/eventos
fechados ainda precisam de uma política de versão e auditoria própria; não são
apresentadas como concluídas por este relatório.

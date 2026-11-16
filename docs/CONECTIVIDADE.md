# Conectividade e custódia

```text
EdgeBuffer (outbox SQLite) -> ConnectivityManager -> HTTP / Mule / stubs
                                      |
                                      +-> ACK válido -> libera a outbox
Data Mule: cópia durável -> backend -> ACK -> origem e Mule
```

O manager escolhe o caminho. Ele não possui a outbox e nenhum provider pode
apagar mensagens. A liberação exige compatibilidade de `message_id`,
`device_id`, `sequence_number` e `payload_hash`.

| Provider | Estado | Limite desta etapa |
| --- | --- | --- |
| `http` | real no contrato atual | POST individual e credencial do dispositivo |
| `mule` | adaptador lógico | transporte de rede fora de S7-T1/S7-T2 |
| `mqtt` | não registrado | não é transporte validado nesta etapa |
| `lora` | stub indisponível | sem rádio físico |
| `sat_sim` | test double SIMULADO | orçamento simulado, sem cobrança real |

A política versionada está em `connectivity/policy.py`. Classes A, B e C têm
ordem própria, limite de payload, TTL e, para A, orçamento de satélite
simulado. Provider ausente ou indisponível é ignorado com motivo no log.

O Mule persiste sua cópia antes de confirmar a coleta. A origem mantém a
mensagem na outbox. `custody_status=COLETADO` só vira `ACKED` após confirmação
compatível; `origin_buffer` pode receber a mesma confirmação e liberar a cópia
da origem. `custody_token` correlaciona origem, Mule, mensagem e hash.

```powershell
venv\Scripts\python.exe -m unittest simulators.test_edge_client simulators.test_transbordo_mule_client
venv\Scripts\python.exe manage.py test api_tcc.tests.test_data_mule_integration
```

Esses testes não provam rede rural, rádio, satélite ou operação de campo.


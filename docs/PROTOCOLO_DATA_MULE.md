# S8-T4 — PoC de Data Mule

## Estado

PoC de software implementada e testada. O encontro entre a colhedora e o
transbordo é uma chamada Python; não há rádio, ESP-NOW, descoberta física ou
comunicação entre ESP32 neste cenário.

## Fluxo demonstrado

```text
colhedora -> outbox SQLite local
          -> coleta lógica
transbordo -> buffer SQLite independente
           -> endpoint real /api/telemetria/
backend    -> deduplicação e persistência
```

O transbordo nunca substitui `device_id`. `message_id`, `sequence_number` e
`payload_hash` são copiados e validados antes da persistência no buffer. O
segundo encontro reconhece a chave `(device_id, message_id)` e não cria outra
mensagem. Uma divergência de hash gera conflito explícito e preserva a cópia
existente.

O ACK de coleta significa apenas que a cópia está persistida no buffer do
transbordo. A leitura original permanece na outbox da colhedora. O ACK do
backend é uma etapa separada e somente ele muda o estado da cópia do
transbordo para `SINCRONIZADA`.

## Arquivos

- `simulators/transbordo_mule_client.py`: `MuleBuffer`, coleta, idempotência,
  retry, prioridade A/B/C e sincronização pelo endpoint real.
- `simulators/edge_client.py`: pequena interface `transfer_candidates()` e
  parâmetro `source` em `generate_payload()`.
- `simulators/test_transbordo_mule_client.py`: testes do buffer e do cliente.
- `api_tcc/tests/test_data_mule_integration.py`: teste com `APIClient` Django,
  passando pelo endpoint e pelo serviço de ingestão.

## Execução

Para demonstrar somente geração, persistência e encontro repetido sem backend:

```powershell
$env:PYTHONPATH = "simulators"
.\venv\Scripts\python.exe simulators\transbordo_mule_client.py `
  --count 20 --offline --repeat-encounter `
  --edge-buffer-path .\tmp\colhedora.db `
  --mule-buffer-path .\tmp\transbordo.db
```

Para sincronizar com o backend em execução, forneça a chave já configurada no
ambiente e remova `--offline`:

```powershell
$env:FIELDNODE_API_KEY = "<chave configurada no ambiente>"
.\venv\Scripts\python.exe simulators\transbordo_mule_client.py `
  --count 20 --repeat-encounter
```

O script não executa o cliente de sincronização direta da colhedora no modo
Data Mule. Os bancos locais usados na demonstração são temporários e não devem
ser versionados.

## Verificação realizada em 9 de outubro de 2026

- `pytest simulators/test_edge_client.py simulators/test_transbordo_mule_client.py -q` — **8 passaram**.
- `manage.py test api_tcc.tests.test_data_mule_integration` — **1 passou**.
- O teste Django criou 20 leituras no endpoint, confirmou `source=data_mule`,
  encontrou os 20 `message_id` e preservou `device_id=COLH-DATA-MULE-01`.
- Foram observados avisos de compatibilidade do scikit-learn durante o teste
  Django; eles não impediram a execução nem alteraram o resultado aprovado.

## Limitações e segurança

Esta PoC não valida proximidade, alcance, interferência, ESP-NOW, pareamento,
autenticação física, extração de chave, comunicação entre veículos ou operação
agrícola. `device_id` identifica a origem dos dados, mas não autentica sozinho
o dispositivo. O backend continua usando o contrato atual de `X-API-Key`.

`source=data_mule` é usado neste cenário para registrar o caminho de transporte
da PoC. Como o campo aceita texto livre no serviço atual, não foi criada uma
migration ou uma tabela nova. A semântica deverá ser formalizada antes de uma
integração física real, junto com identidade por dispositivo, rotação de
credenciais e proteção de integridade.

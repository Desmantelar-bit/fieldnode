# S2-T8 — Credencial HTTP por dispositivo e STRIDE

## Diagnóstico e decisão

Antes, `HasIngestionCredential` delegava a uma permissão que aceitava `FIELDNODE_API_KEY` global e um mapa estático em configuração. Os dois endpoints HTTP de ingestão usavam essa permissão. `simulators/edge_client.py`, `simulators/transbordo_mule_client.py` e scripts de simulação/teste também usavam `X-API-Key`. O payload era validado para chaves estáticas configuradas por ID, mas uma chave global não tinha identidade própria.

A S2-T1 já tinha `Machine.external_code` como identidade e um `DeviceCredential` ligado ao username/hash MQTT do Mosquitto. Reutilizei esse registro, sem modelo de identidade duplicado, adicionando campos próprios `http_*`. Credenciais HTTP e MQTT mantêm hashes e estados independentes; revogar um canal não revoga implicitamente o outro.

## Implementação

- `X-Device-Id` e `X-Device-Key` autenticam ingestão individual e em lote. SHA-256 deriva o digest de uma chave aleatória de 32 bytes representada em URL-safe Base64; `hmac.compare_digest` compara o digest. O banco não recebe a chave em claro.
- O backend exige igualdade entre identidade autenticada, `device_id` e `maquina_id` em todos os itens antes de persistir. Divergência responde 403; credencial ausente, inválida ou revogada responde 401.
- `http_last_seen_at` é atualizado com intervalo mínimo de cinco minutos. A rotação mantém somente o digest anterior por até 24h; após o prazo ele é rejeitado e removido na tentativa de autenticação subsequente.
- Provisionamento: `python scripts/provision_device.py <device_id> --http`; rotação: `--http --rotate`; revogação: `--http --revoke`. A máquina deve existir. A chave é exibida uma vez. Eventos criados/rotacionados/revogados são auditados.
- O provisionador MQTT também audita as ações, sem inserir senha ou hash no registro de auditoria.
- `FIELDNODE_API_KEY` só pode autenticar no perfil DEBUG com `ALLOW_LEGACY_INGESTION_KEY=True`; não há fallback global em ambiente `DEBUG=False`. O mapa legado de chaves deixou de ser lido do ambiente. Uma compatibilidade só existe quando testes antigos injetam explicitamente o mapa em runtime sob DEBUG; clientes operacionais usam headers individuais.
- `edge_client.py` e `transbordo_mule_client.py` usam `FIELDNODE_DEVICE_KEY` e headers individuais. O simulador MQTT que tem fallback HTTP recebe mapa local por dispositivo via `FIELDNODE_HTTP_DEVICE_KEYS`.
- `docs/SEGURANCA.md` documenta a decisão de identidade compartilhada, controles e riscos STRIDE. Flash Encryption está planejada para S8, não implementada; não houve configuração irreversível de hardware.

## Testes e verificações

VERIFICADO: `test_s2_t7_t8.py` cobre autenticação individual, anti-spoof sem persistência, chave global fora de DEBUG, chave global em DEBUG, rotação, aceitação da chave anterior durante a janela, expiração da chave anterior, revogação, imutabilidade ORM e permissões read-only do Admin.

VERIFICADO: `test_telemetria.py`, `test_week2_security.py`, `test_decisions.py` e `test_s2_t7_t8.py` passaram juntos após atualizar o teste de identidade cruzada para esperar 403.

VERIFICADO: `manage.py check` e `makemigrations --check --dry-run` passaram.

NÃO VERIFICADO: a suíte inteira não pôde ser coletada porque `api_tcc/tests/test_s1_t5_temporal_contract.py` importa `DeviceClockAnchor`, ausente em `api_tcc.models`. A falha de importação é anterior à execução dos testes de S2-T7/T8.

NÃO VERIFICADO: hardware ESP32 físico. Não há evidência de firmware atualizado com headers individuais. Credencial extraída da flash ainda permite falsificação até revogação; Flash Encryption permanece requisito planejado para S8.

## Evidência de segredo e limites

O código guarda apenas SHA-256 para HTTP, não imprime chave em logs e passa chave em claro somente ao solicitante do comando de provisionamento. O teste verifica comportamento HTTP, não faz uma captura completa de logs do processo externo de provisionamento.

Risco residual: comprometimento da chave individual permite forjar a identidade correspondente; o dispositivo continua sendo autoridade sobre as leituras que assina/enviará. SHA-256 pressupõe chave de alta entropia. Administração do banco pode adulterar o cadastro ou auditoria. Não foi validado transporte TLS de ESP32 nem Flash Encryption.

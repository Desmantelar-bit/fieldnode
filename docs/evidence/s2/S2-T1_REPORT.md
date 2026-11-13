# S2-T1 — MQTT com ACL por dispositivo e anti-spoof

**Status: PARCIAL (configuração e validação da aplicação implementadas; broker real não verificado).**

## Estado anterior observado

- `allow_anonymous false` estava ativo. `mosquitto.conf` escutava em `0.0.0.0:1883` dentro do container; Compose publicava a porta somente em `127.0.0.1:1883` no host.
- Compose criava um único usuário/senha MQTT compartilhado no início do broker com `mosquitto_passwd -b`; não havia ACL.
- O worker assinava `fieldnode/#` e só configurava autenticação quando as duas env vars globais existiam.
- `device_id` e o contrato S1-T5 já existiam em `LeituraTelemetria`/payload. Não havia `DeviceCredential` nem entidade `Device` separada.
- `HasIngestionCredential` já valida `device_id` contra `FIELDNODE_DEVICE_API_KEYS` em credenciais individuais HTTP; a chave HTTP global legada não é identidade individual.

## Alterações

- `DeviceCredential` armazena `device_id`, username, hash Django da credencial, status, provisionamento e datas de ciclo de vida. Senha de dispositivo é aleatória, apresentada uma vez pelo provisionador e não persiste no banco.
- `mosquitto/acl.conf` separa worker e dispositivos. O worker lê `fieldnode/+/telemetria` e `fieldnode/+/status`, escreve `fieldnode/_ack/#`; `%u` permite a cada dispositivo escrever apenas `fieldnode/%u/telemetria` e `fieldnode/%u/status`, e ler apenas `fieldnode/_ack/%u`.
- `mosquitto.conf` aponta para `acl_file` e para password file dedicado. Compose monta ACL e diretórios de segredo como somente leitura no container; worker recebe somente seu arquivo secreto, sem o password file.
- O entrypoint do broker exige os arquivos já provisionados, copia o password file para o volume privado `/mosquitto/data` e atribui propriedade ao UID/GID 1883 antes de iniciar. Ele não recria usuários nem injeta senha em argumentos/env. Compose não injeta credenciais MQTT no web/worker.
- `scripts/provision_mqtt_worker.py` prepara o usuário próprio do worker. `scripts/provision_device.py <device_id>` provisiona; `--rotate` rotaciona; `--revoke` remove o usuário do password file e marca a credencial revogada. O password file é atualizado por substituição de arquivo, sem senha em argumentos do processo. Se o broker estiver ativo, é reiniciado para derrubar sessões já autenticadas.
- `scripts/provision_demo.py` provisiona individualmente `COLH-01` a `COLH-08`, IDs existentes em `scripts/simular_mqtt.py`; oferece rotação e revogação em lote sem senha universal.
- O callback valida tópico e JSON, confere credencial ativa e compara `payload.device_id` com o ID do tópico. `maquina_id` não é usado como identidade. Spoof gera `DeadLetterEntry(contexto="MQTT_SPOOF")` com metadados limitados, antes de qualquer ingestão.
- O worker falha antes de construir/conectar o cliente caso falte sua credencial. Não há fallback anônimo, inclusive em DEBUG.

## Evidências de teste

- Os testes Django direcionados cobriram anti-spoof com DLQ e ausência de ingestão, credencial revogada, tópico malformado, JSON inválido e worker sem segredo. Eles passaram na execução combinada de 85 testes (os dois únicos erros dessa execução foram expectativas antigas de strings de ACK em `test_integration.py`).
- A execução posterior das suítes de segurança, autenticação, correlação, decisões agentivas e permissões terminou com **77 testes aprovados**.
- `python -m py_compile` passou nos módulos Python alterados.
- **NÃO VERIFICADO:** publicação permitida/negada contra Mosquitto, `Denied PUBLISH`, leitura cruzada de ACK, autenticação inválida no broker e efeito de reload/restart. Não foi capturado log do broker.
- **NÃO VERIFICADO:** o password file foi criado e ACL carregada por um broker em execução. A imagem é `eclipse-mosquitto:2`, mas a versão efetiva do container não foi lida. O Compose só inicia depois de preparar os diretórios locais por `provision_mqtt_worker.py` e provisionar os dispositivos.
- **NÃO VERIFICADO:** perfil demo provisionado com credenciais reais de bancada. Nenhum segredo de demo foi criado neste trabalho.

## Limitações

- A infraestrutura não possui um registro de dispositivo preexistente; a criação controlada via CLI cria `DeviceCredential`. Não há vínculo `DeviceCredential → Machine`, pois a identidade de dispositivo é distinta do código legado de máquina e ainda não existe mapeamento de domínio explícito.
- Transporte MQTT continua sem TLS; autenticação/ACL não protegem contra interceptação no segmento. HTTPS local permanece no escopo S13-T12/D-35.
- O arquivo local do worker é um segredo Docker ignorado pelo Git, mas sua proteção em repouso depende das permissões do host.
- A sincronização do cadastro HTTP via `FIELDNODE_DEVICE_API_KEYS` ainda é configuração separada; a migração para uma fonte persistida compartilhada não foi feita nesta tarefa.

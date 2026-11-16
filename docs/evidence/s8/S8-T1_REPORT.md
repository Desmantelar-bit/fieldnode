# S8-T1 - Relatório de evidência

## Estado honesto

**IMPLEMENTADO em software:** estrutura PlatformIO, firmware ESP32 para
DS18B20/MQTT, NVS de sequência, `boot_id`, validação de leitura, LED de estado,
segredos fora do Git, gerador do header de severidade e testes nativos.

**NÃO VERIFICADO:** compilação PlatformIO nesta máquina (a instalação do
PlatformIO ocorreu, mas os downloads das plataformas `native` e `espressif32`
não concluíram), placa física, sensor,
publicação MQTT real, ACL com credencial provisionada, ingestão em banco,
`data_origin=medido`, desconexão física e reconexão em bancada. Não há hardware
ou `pio` disponível no checkout usado nesta execução.

## Contrato aplicado

O payload segue `docs/CONTRATO_TELEMETRIA_V1.md`: `device_id`, `maquina_id`,
`message_id`, `sequence_number`, `boot_id`, `uptime_ms`, `time_source`,
`schema_version`, temperatura em °C, vibração em `indice_0_10`, RPM, `source` e
`transport`. O firmware publica `time_source=unsynced` porque não inventa hora.
O backend MQTT agora repassa o `topic_device` autenticado para
`registrar_leitura`, permitindo `data_origin=medido` somente após autenticação.

## Arquivos

- `firmware/platformio.ini`
- `firmware/src/main.cpp`
- `firmware/include/config.h`
- `firmware/include/secrets.example.h`
- `firmware/include/severity_contract.h`
- `firmware/lib/telemetry_core/*`
- `firmware/test/native/test_telemetry_core.cpp`
- `firmware/README.md`
- `scripts/generate_firmware_contract.py`
- `.github/workflows/contracts.yml`
- `api_tcc/management/commands/mqtt_listen.py`

## Comportamento delimitado

`-127.0`/`DEVICE_DISCONNECTED_C`, NaN, valores fora do contrato e RPM fora da
faixa não viram leitura. A sequência só avança depois de `mqtt.publish` aceitar
a mensagem e é salva em NVS. Falha de transporte não é chamada de ACK. Esta
entrega não cria uma segunda outbox: retenção offline completa permanece em
S8-T4.

## Verificações executadas

- `venv\Scripts\python.exe scripts\generate_firmware_contract.py --check`:
  passou.
- compilação direta da biblioteca C++ de núcleo com `g++ -Wall -Wextra
  -Werror`: passou; o teste executável equivalente também passou antes da
  configuração Unity do PlatformIO.
- `venv\Scripts\python.exe manage.py check`: passou.
- `venv\Scripts\python.exe manage.py test
  api_tcc.tests.test_week2_security.MqttIdentityBoundaryTests
  api_tcc.tests.test_data_origin --verbosity 0`: 8 testes passaram.
- `git diff --check`: passou, com apenas avisos de normalização LF/CRLF do
  Git nos documentos existentes.
- `pio test -d firmware -e native` e `pio run -d firmware -e esp32dev` foram
  iniciados, mas ficaram bloqueados durante a instalação/download das
  plataformas; build PlatformIO permanece pendente de execução na CI ou em
  uma máquina com cache de toolchains.

## Pendências físicas

Confirmar modelo da placa e GPIO do LED, montar DS18B20 com pull-up de 4,7 kΩ,
provisionar credencial MQTT individual, executar `pio run`, testar ACL,
`mosquitto_sub`, `mqtt_listen`, persistência com `data_origin=medido`, sensor
desconectado e reconexão. Compilação ou teste de host não substituem esse
ensaio. Sem foto, log serial e registro no banco, a tarefa não deve ser
classificada como validada no fluxo real.

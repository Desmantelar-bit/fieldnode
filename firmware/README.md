# Firmware FieldNode

[![Firmware CI](https://github.com/Desmantelar-bit/fieldnode/actions/workflows/firmware.yml/badge.svg)](https://github.com/Desmantelar-bit/fieldnode/actions/workflows/firmware.yml)

Primeiro fluxo de bancada: DS18B20 -> ESP32 -> Wi-Fi -> Mosquitto ->
`mqtt_listen` -> banco. O projeto usa PlatformIO e o ambiente padrão
`esp32dev`; confirme o modelo da placa antes de compilar para hardware real.

## Configuração local

Copie `include/secrets.example.h` para `include/secrets.h` e preencha a
credencial individual provisionada para o `FIELDNODE_DEVICE_ID`. O arquivo
real não deve ser versionado. MQTT nesta bancada não usa TLS, conforme a
limitação documentada em `docs/SEGURANCA.md`.

## Ligações de referência

- DS18B20 VDD -> 3V3
- DS18B20 GND -> GND
- DS18B20 DATA -> GPIO 4
- resistor de 4,7 kΩ entre DATA e 3V3
- LED onboard -> GPIO 2, sujeito à confirmação da placa

## Comandos

```powershell
pio run -e esp32dev
pio test -e native
```

O ambiente `esp32dev` gera `firmware/.pio/build/esp32dev/firmware.bin`. O
ambiente `native` executa os testes host-side sem placa física. O CI copia
`include/secrets.example.h` para `include/secrets.h` apenas no runner, compila o
firmware, executa os testes e publica o `.bin` com SHA-256. O artefato é um
build de CI; não é certificado nem validado em hardware de campo.

Para instalar o CLI usado pelo CI:

```powershell
python -m pip install platformio==6.1.16
```

O workflow `Firmware CI` roda em pull requests para `main`, pushes em `main` e
execução manual. A proteção da branch precisa exigir o check `Build and host
tests`; criar o workflow, por si só, não protege `main`.

O firmware usa NVS para a sequência e gera um `boot_id` novo a cada boot. Sem
RTC/NTP, publica `time_source=unsynced` e `uptime_ms`; não inventa timestamp.
Não existe outbox persistente de amostras nesta etapa. Falha de Wi-Fi/MQTT não
é reportada como ingestão bem-sucedida.

O DS3231 usa `0x68`; o MPU6050 foi configurado em `0x69` via AD0 para evitar
colisão no I2C. A seleção da fonte verifica OSF e só aceita `rtc` após evidência
persistida. A sincronização por gateway tem API interna, mas ainda depende de
um consumidor MQTT autenticado, que permanece pendente.

O `data_origin=medido` é decidido no backend somente após a autenticação da
credencial individual do MQTT. Um payload parecido, sem identidade autenticada,
não ganha esse selo por declarar um campo no JSON.

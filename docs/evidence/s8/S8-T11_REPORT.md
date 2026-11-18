# S8-T11 · relatório de execução

## Estado

**IMPLEMENTADO EM CÓDIGO / TESTADO EM HOST / BANCADA FÍSICA PENDENTE.**

## Arquitetura

- `firmware/lib/rpm`: contador por interrupção, debounce configurável, janela
  fixa e cálculo fora da ISR.
- `firmware/lib/gps`: parser UART incremental com TinyGPSPlus e política de
  fix, HDOP e idade dos dados.
- `firmware/src/main.cpp`: GPIO 27 para RPM, UART1 RX16/TX17 a 9600 baud,
  `rpm` somente quando a janela é válida e GPS sem fix sem posição/velocidade.
- `contracts/telemetry.v1.2.json`: RPM, GPS e campos de posição opcionais.
- `api_tcc/services/telemetria.py`: ausência preservada; valores finitos e
  limites validados.

## Host e bancada

Os testes host cobrem três frequências sintéticas, divisão inválida e qualidade
GPS. Não houve gerador de pulsos, ESP32, sensor Hall/óptico, módulo GPS ou vídeo
disponível nesta execução. Logo, erro físico de RPM, primeiro fix, HDOP medido e
recuperação em bancada estão **NÃO VERIFICADOS**.

## Limitações explícitas

Os GPIOs e o baud são configuração de bancada, não comprovação da placa ou do
módulo físico. O limite de 500 us precisa ser confrontado com RPM máximo e
pulsos por volta. O módulo não altera `event_time`, `boot_id`, `uptime_ms` ou
`time_source`.

## Aceite

Host: **VERIFICADO**, `pio test -e native` passou com 8/8 casos e os testes
Python direcionados passaram. O build do alvo `esp32dev` ficou **NÃO
VERIFICADO** porque o PlatformIO permaneceu instalando `espressif32@6.6.0` e
não concluiu no ambiente. Bancada e máquina são roadmap, condicionados à
compra, montagem segura, tabela de calibração e vídeo.

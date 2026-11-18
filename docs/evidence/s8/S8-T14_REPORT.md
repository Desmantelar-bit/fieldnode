# S8-T14 - Relatório de execução

## Estado

**PROTOCOLO IMPLEMENTADO; INTEGRAÇÃO FÍSICA PENDENTE.**

## Auditoria inicial

- Foram revisados `docs/BOM.md`, `docs/HARDWARE.md`, `firmware/include/config.h`,
  `firmware/src/main.cpp`, `firmware/platformio.ini` e os relatórios S8-T10 a
  S8-T13.
- O firmware possui DS18B20, RTC, sequência persistente, MQTT, RPM, GPS, SPC e
  alarme local em configuração de bancada.
- S8-T11 registra host verificado e bancada pendente.
- S8-T12 registra CAN somente escuta verificado em host e veículo real pendente.
- S8-T13 registra 11/11 testes nativos e demonstração física pendente.
- S8-T10 registra zero componentes comprados/recebidos/testados comprovados.

## Arquivos criados

- `docs/INTEGRACAO_HARDWARE.md`
- `docs/evidence/s8/S8-T14_REPORT.md`
- `firmware/tests/bancada/README.md`
- oito checklists em `firmware/tests/bancada/`
- `firmware/tests/bancada/validate_s8_t14.py`, que valida a estrutura documental
  sem simular ou aprovar ensaio físico

## Estado dos degraus

| Degrau | Estado | Evidência | Lacuna principal |
|---|---|---|---|
| D1 | PENDENTE | código/teste host | sensor e placa reais |
| D2 | PENDENTE | código MQTT | publicação física |
| D3 | PENDENTE | contrato/backend | origem física persistida |
| D4 | PENDENTE | código RTC/NVS | reboot físico |
| D5 | PENDENTE/BLOQUEADO | biblioteca presente | 50 cortes físicos e ACK |
| D6 | PENDENTE | biblioteca ESP-NOW | segundo ESP32 e PER |
| D7 | BLOQUEADO | nenhum módulo comprovado | hardware e configuração LoRa |
| D8 | PENDENTE | testes SPC/alarme host | periféricos e gateway desligado |

Nenhum degrau foi marcado como aprovado.

## Verificações executadas

`venv\Scripts\python.exe firmware/tests/bancada/validate_s8_t14.py` passou,
confirmando o protocolo, os oito cabeçalhos e os oito checklists.

`pio test -e native` executado em `firmware/` passou com **11/11 casos**. Esse
resultado é teste host do firmware e não altera o estado físico dos degraus.

Nenhum teste físico foi executado nesta tarefa. A classificação acima é baseada
nos relatórios existentes e em inspeção documental do checkout. A verificação
de software específica de S8-T14 é a presença dos documentos e checklists; ela
não substitui os ensaios descritos por degrau.

## Lacunas e próximo passo

O próximo passo operacional é preencher a BOM com recebimento real e executar
D1. Depois disso, preservar logs, fotos e responsáveis no histórico do protocolo.

## Honestidade do aceite

O protocolo está preparado e preenchido com o estado conhecido. A integração
física, validação de campo e aprovação dos oito degraus continuam pendentes.

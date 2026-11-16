# Reposicionamento do escopo de hardware

Este documento separa o que o checkout demonstra em software e bancada do que
depende de placa, instrumento, máquina agrícola ou operação de campo.

## A. Implementado e comprovado no checkout

| Componente | Estado verificável | Evidência | Limitação |
|---|---|---|---|
| Firmware PlatformIO | Código para `esp32dev`, com configuração e dependências declaradas | `firmware/platformio.ini`, `firmware/src` | Build local/CI pendente; não comprova a placa exata nem operação prolongada |
| Testes host-side | Ambiente `native` e testes Unity existentes | `firmware/test/native`, `pio test -e native` | Não substitui periféricos ESP32 físicos |
| Credencial individual | Backend usa identidade por dispositivo, hash, rotação e revogação | `docs/evidence/s2/S2-T8_REPORT.md`, `docs/SEGURANCA.md` | A chave do firmware não está protegida contra extração de flash |
| Contratos de protocolo | Lógica de telemetria, ESP-NOW e J1939 presente no firmware e testável no host | `firmware/lib`, testes nativos existentes | Não comprova rádio, CAN ou sensor conectado |

## B. Protótipo ou bancada

- DS18B20 -> ESP32 -> Wi-Fi -> MQTT é um fluxo de bancada, condicionado a placa,
  sensor, broker e logs físicos correspondentes.
- ESP-NOW e gateway são fronteiras de integração de bancada. PER, alcance,
  obstáculos, reenvio e ACK de aplicação estão **NÃO VERIFICADOS** sem ensaio
  com placas e logs.
- Outbox, persistência local e retenção só podem ser declaradas até o limite
  medido. Não há base para chamar o armazenamento de buffer de 30 dias sem
  part number, taxa de amostragem e ensaio de desgaste.

## C. Roadmap

- Flash Encryption e Secure Boot em placa dedicada, após plano de recuperação.
- TLS no transporte do firmware e estratégia de assinatura de payloads, se
  exigidos pelo cenário de implantação.
- OTA segura, atualmente **DEFER**, com assinatura, rollback, revogação e
  recuperação comprovados.
- Integração com ECUs reais, CAN/J1939 em máquina agrícola e validação de
  sensores no ambiente de operação.
- Operação prolongada em campo, alcance de rádio e autonomia de armazenamento.
- Proteção física contra extração e adulteração.

## Decisão de segurança do dispositivo

As credenciais são individuais no backend conforme S2-T8, mas a credencial
armazenada no firmware de bancada permanece exposta a extração física enquanto
Flash Encryption não estiver ativa. A extração pode permitir falsificação da
identidade daquele dispositivo até a revogação. Não se afirma proteção contra
extração, Secure Boot, Flash Encryption ou OTA segura.

Flash Encryption e Secure Boot são `ARCHITECT_NOW`: o desenho, o checklist e os
critérios de recuperação ficam definidos agora. A execução é `DEFER` para uma
placa dedicada. Não gravar eFuses, não provisionar chaves definitivas e não
bloquear debug na placa de demonstração.

Checklist mínimo antes da ativação:

1. identificar chip e revisão;
2. revisar documentação oficial do fabricante;
3. preparar firmware mínimo de recuperação;
4. definir chave de assinatura, backup e acesso;
5. executar provisionamento controlado;
6. testar boot de firmware válido;
7. testar rejeição de firmware inválido;
8. testar atualização, falha e recuperação;
9. validar armazenamento e partições;
10. documentar substituição da placa;
11. registrar o estado das eFuses;
12. obter aprovação explícita antes de qualquer operação irreversível.

## BOM

O inventário real está em [`docs/BOM.md`](BOM.md). Nenhum fornecedor, data ou
custo foi inferido a partir do código.

# S8-T7 - CAN/J1939 em bancada com emissor de teste

O decodificador puro e os testes host-side foram implementados. A validação elétrica
com ESP32/TWAI ou MCP2515 e emissor independente **não foi executada**. Qualquer resultado
desta tarefa deve ser descrito como **bancada com emissor J1939 de teste**, nunca como
compatibilidade com máquina ou fabricante real.

| Recurso | Estado |
|---|---|
| ID estendido de 29 bits e PGN PDU1/PDU2 | IMPLEMENTADO / TESTADO EM HOST |
| EEC1, ET1, EFL/P1 e DM1 | IMPLEMENTADO / TESTADO EM HOST |
| indisponível/reservado não vira número | IMPLEMENTADO / TESTADO EM HOST |
| fixture `j1939_v1` | IMPLEMENTADO, sintética de bancada |
| leitura CAN física | VALIDATE_NOW |
| evento Django `Event` a partir de frame físico | ROADMAP |
| compatibilidade com máquina real | ROADMAP / FORA DO ESCOPO |

As fontes públicas e as limitações estão em `firmware/lib/j1939/README.md`.
Os mappings legados de `case_ih_v1` e `john_deere_v1` continuam preservados por
compatibilidade com testes existentes, mas não são evidência de integração física.

Pendências: identificar placa/transceiver; decidir TWAI ou MCP2515; configurar velocidade,
terminação e pinos; transmitir quadros por emissor independente; capturar serial/CAN; e
registrar a comparação com payload simulado equivalente.
